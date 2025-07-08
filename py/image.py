from comfy.comfy_types import IO
from comfy.utils import ProgressBar
from .fields import Field
from .utils import category, endpoint

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from itertools import product
import colorsys


# ===============================================
# Image Flip
# ===============================================
class ImageFlip:
    @classmethod
    def INPUT_TYPES(cls): 
        return {
            "required": {
                "images": Field.image(), 
                "axis": Field.combo(["none", "x", "y"])
            }
        }
    
    RETURN_TYPES = (IO.IMAGE, )
    CATEGORY = category
    FUNCTION = "execute"
    
    def execute(self, images: torch.Tensor, axis: str):
        """
        画像反転
        images: shape [B, H, W, C]
        axis: x or y or both
        """
        
        if axis == "x":
            output = torch.flip(images, dims=[2])
        elif axis == "y":
            output = torch.flip(images, dims=[1])
        else:
            output = images
        
        return (output, )



# ===============================================
# Perfect Pixel
# ===============================================
class PerfectPixel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": Field.image(), 
                "pixel_size": Field.int(default=8, min=1), 
                "enable_reduce": Field.boolean(), 
                "max_colors": Field.int(default=64, min=1), 
                "threshold": Field.float(default=8, min=0), 
                "space": Field.combo(["RGB", "HSV"]), 
            }
        }
        
    RETURN_TYPES = (IO.IMAGE, )
    CATEGORY = category
    FUNCTION = "execute"
    
    def kCentroid(self, image: Image, width: int, height: int, centroids: int):
        image = image.convert("RGB")
        downscaled = np.zeros((height, width, 3), dtype=np.uint8)

        wFactor = image.width / width
        hFactor = image.height / height
        
        for x, y in product(range(width), range(height)):
            tile = image.crop((x*wFactor, y*hFactor, (x*wFactor)+wFactor, (y*hFactor)+hFactor))
            tile = tile.quantize(colors=centroids, method=1, kmeans=centroids).convert("RGB")

            color_counts = tile.getcolors()
            most_common_color = max(color_counts, key=lambda x: x[0])[1]

            downscaled[y, x, :] = most_common_color
        
        return Image.fromarray(downscaled, mode="RGB")
    
    
    def color_distance(self, c1, c2, space):
        if space == "HSV":
            c1 = colorsys.rgb_to_hsv(*[x / 255.0 for x in c1])
            c2 = colorsys.rgb_to_hsv(*[x / 255.0 for x in c2])
            dh = min(abs(c1[0] - c2[0]), 1.0 - abs(c1[0] - c2[0]))
            ds = abs(c1[1] - c2[1])
            dv = abs(c1[2] - c2[2])
            return (dh ** 2 + ds ** 2 + dv ** 2) ** 0.5
        else: # RGB
            return np.linalg.norm(np.array(c1) - np.array(c2)) / 255.0
    
    
    def flood_color_fill(self, image: Image, threshold: float, space: str):
        arr = np.array(image)
        h, w, _ = arr.shape
        visited = np.zeros((h, w), dtype=bool)
        output = np.copy(arr)

        for y in range(h):
            for x in range(w):
                if visited[y, x]:
                    continue
                
                base_color = tuple(arr[y, x])
                color_mask = np.zeros((h, w), dtype=bool)

                for j in range(h):
                    for i in range(w):
                        if not visited[j, i]:
                            dist = self.color_distance(base_color, tuple(arr[j, i]), space)
                            if dist <= threshold:
                                color_mask[j, i] = True
                                visited[j, i] = True
                
                # 近い色全てを基準色で塗りつぶす
                output[color_mask] = base_color
        
        return Image.fromarray(output)
    

    def execute(self, images: torch.Tensor, pixel_size: int, enable_reduce: bool, max_colors: int, threshold: float, space: str):
        """
        images: [B, H, W, C]
        """
        output = []
        for image in images:
            image_np = image.cpu().numpy()
            pil_image = Image.fromarray((image_np * 255).astype(np.uint8))

            # 計算する縮小サイズ
            new_width = pil_image.width // pixel_size
            new_height = pil_image.height // pixel_size
            
            # kCentroidでダウンスケール
            downscaled = self.kCentroid(pil_image, new_width, new_height, 2)
            
            # 減色
            if enable_reduce:
                downscaled = downscaled.quantize(colors=max_colors, method=1, kmeans=max_colors, dither=0).convert("RGB")
                downscaled = self.flood_color_fill(image=downscaled, threshold=threshold, space=space)

            out_np = np.array(downscaled).astype(np.float32) / 255.0
            out_tensor = torch.from_numpy(out_np)
            output.append(out_tensor)
        
        new_image = torch.stack(output)
        return (new_image, )



# ===============================================
# Get Image Side
# ===============================================
class GetImageSide:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": Field.image(), 
                "side": Field.combo(["short", "long"])
            }
        }
    
    RETURN_TYPES = (IO.INT, IO.INT, IO.INT)
    RETURN_NAMES = ("width", "height", "side")
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, image: torch.Tensor, side: str):
        height, width = image.shape[1], image.shape[2]
        
        if side == "short":
            side = min(width, height)
        
        else:
            side = max(width, height)
        
        return (int(width), int(height), int(side))


# ===============================================
# Pixel Resize for Wan
# ===============================================
class PixelResizeForWan:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": Field.image(), 
                "target": Field.int(default=704, step=8, min=480), 
                "pad_color": Field.combo(["black", "white", "grey"])
            }
        }
    
    RETURN_TYPES = (IO.IMAGE, IO.INT)
    RETURN_NAMES = ("images", "scale")
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, images: torch.Tensor, target: int, pad_color: str):
        """
        目的: 画像の長辺をtargetになるように画像を整数倍に拡大
        拡大方法はnearest-exact
        Step1: 1/8に縮小(入力画像は8倍されたドット絵を想定)
        Step2: 整数倍
        Step3: 長辺がtargetになるように長辺方向だけパディング
        Step4: 短辺は最も近い16の倍数にパディング
        
        短辺 -> smallを整数倍
        長辺 -> target
        の画像が得られる
        """
        
        pad_color_map = {
            "black": [0, 0, 0], 
            "white": [1, 1, 1], 
            "grey": [0.5, 0.5, 0.5]
        }
        pad_color = pad_color_map.get(pad_color, [0, 0, 0])
        
        # Stage1: 1/8に縮小
        images = images.permute(0, 3, 1, 2) # BHWC -> BCHW
        small = F.interpolate(images, scale_factor=1/8, mode="nearest-exact")
        _, _, small_H, small_W = small.shape
        
        # Stage2: 整数倍スケーリング
        long_edge = max(small_H, small_W)
        scale = target // long_edge
        scaled = F.interpolate(small, scale_factor=scale, mode="nearest-exact")
        _, _, H, W = scaled.shape

        # Stage3: 長辺のみのパディング
        pad_color_tensor = torch.tensor(pad_color, dtype=scaled.dtype, device=scaled.device).view(1, 3, 1, 1)
        if H > W: # 縦長
            pad_total = target - H
            pad_top = pad_total // 2
            pad_bottom = pad_total - pad_top
            padding = [0, 0, pad_top, pad_bottom]
            
            padded = F.pad(scaled, padding, mode="constant", value=0)
            if pad_top > 0:
                padded[:, :, :pad_top, :] = pad_color_tensor
            if pad_bottom > 0:
                padded[:, :, -pad_bottom:, :] = pad_color_tensor
        
        else: # 横長
            pad_total = target - W
            pad_left = pad_total // 2
            pad_right = pad_total - pad_left
            padding = [pad_left, pad_right, 0, 0]
            
            padded = F.pad(scaled, padding, mode="constant", value=0)
            if pad_left > 0:
                padded[:, :, :, :pad_left] = pad_color_tensor
            if pad_right > 0:
                padded[:, :, :, -pad_right:] = pad_color_tensor
        
        # Step4: 短辺方向を16の倍数にパディング
        _, _, final_H, final_W = padded.shape
        pad_h = (16 - (final_H % 16)) % 16
        pad_w = (16 - (final_W % 16)) % 16
        
        pad_top2 = pad_h // 2
        pad_bottom2 = pad_h - pad_top2
        pad_left2 = pad_w // 2
        pad_right2 = pad_w - pad_left2
        
        padded2 = F.pad(padded, [pad_left2, pad_right2, pad_top2, pad_bottom2], mode="constant", value=0)
        
        if pad_top2 > 0:
            padded2[:, :, :pad_top2, :] = pad_color_tensor
        if pad_bottom2 > 0:
            padded2[:, :, -pad_bottom2:, :] = pad_color_tensor
        if pad_left2 > 0:
            padded2[:, :, :, :pad_left2] = pad_color_tensor
        if pad_right2 > 0:
            padded2[:, :, :, -pad_right2:] = pad_color_tensor
        
        output = padded2.permute(0, 2, 3, 1) # BCHW -> BHWC

        return (output, scale)


# ===============================================
# ImagesSampleEvenly
# ===============================================
class ImagesSampleEvenly:
    @classmethod
    def INPUT_TYPES(cls): 
        return {
            "required": {
                "images": Field.image(), 
                "num": Field.int(min=0)
            }
        }
    
    RETURN_TYPES = (IO.IMAGE, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, images: torch.Tensor, num: int):
        if num <= 0:
            return (images, )
        
        if num == 1:
            result = [images[len(images) // 2]]
            output = torch.stack(result)
            return (output, )
        
        lst = []
        for image in images:
            lst.append(image)
        
        # 間隔を計算
        step = (len(lst) - 1) / (num - 1)

        # 等間隔に要素を取得
        result = [lst[round(i * step)] for i in range(num)]

        output = torch.stack(result)
        return (output, )


