import torch
from comfy.comfy_types import IO
from .fields import Field
from .utils import log, category, endpoint


class PixelCleanUp:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": Field.image(upload=False), 
                "pixel_size": Field.int(default=4, min=1), 
            }
        }
    
    RETURN_TYPES = (IO.IMAGE, )
    RETURN_NAMES = ("images", )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, images: torch.Tensor, pixel_size: int):
        output_images = []

        for i in range(images.shape[0]):
            image = images[i]
            h, w, c = image.shape
            processed_image = image.clone()
            
            for y in range(0, h, pixel_size):
                for x in range(0, w, pixel_size):
                    block = image[y:y+pixel_size, x:x+pixel_size, :] # [ps, ps, C]

                    # blockを(色ごとに)一意にして最大数を持つ色を探す
                    flat = block.reshape(-1, c)
                    unique_colors, counts = torch.unique(flat, return_counts=True, dim=0)
                    dominant_color = unique_colors[counts.argmax()]

                    processed_image[y:y+pixel_size, x:x+pixel_size, :] = dominant_color

            output_images.append(processed_image)
        
        res = torch.stack(output_images)

        return (res, )