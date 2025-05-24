import json
import math
from aiohttp import web
from comfy.comfy_types import IO
from nodes import EmptyLatentImage
from .fields import Field
from .utils import log, category, endpoint


ASPECT_RATIOS_PRESETS = [
    "none", 
    "[landscape] 3:1", 
    "[landscape] 12:5", 
    "[landscape] 7:4", 
    "[landscape] 19:13", 
    "[landscape] 3:2", 
    "[landscape] 9:7", 
    "[landscape] 4:3", 
    "[square] 1:1", 
    "[portrait] 3:4", 
    "[portrait] 7:9", 
    "[portrait] 2:3", 
    "[portrait] 13:19", 
    "[portrait] 4:7", 
    "[portrait] 5:12", 
    "[portrait] 1:3", 
]

class AspectRatios:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_resolution": Field.int(default=512, min=0), 
                "round_to": Field.int(default=8, min=1), 
                "aspectW": Field.int(default=1, min=1), 
                "aspectH": Field.int(default=1, min=1), 
                "preset": Field.combo(choices=ASPECT_RATIOS_PRESETS), 
                "batch_size": Field.int(default=1, min=1), 
            }
        }
    
    RETURN_TYPES = (IO.INT, IO.INT, IO.LATENT)
    RETURN_NAMES = ("width", "height", "latent")
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, base_resolution, round_to, aspectW, aspectH, preset, batch_size):
        width, height = calc_resolution(base_resolution, round_to, aspectW, aspectH)
        
        latent = EmptyLatentImage().generate(width, height, batch_size)[0]
        
        return (width, height, latent)



# javasript側で同じ計算をするため計算用関数を分離
def calc_resolution(base, round_to, aspectW, aspectH):
    # 基準面積
    target_area = base ** 2
    
    # アスペクト比を適用
    aspect_ratio = aspectW / aspectH

    # 幅と高さの計算
    width = math.sqrt(target_area * aspect_ratio)
    height = width / aspect_ratio

    # 64の倍数に丸める
    width = math.floor(width / round_to) * round_to
    height = math.floor(height / round_to) * round_to

    return width, height



# endpoint
@endpoint.post("aspect_ratios/calc")
async def endpoint_calc_resolution(req: web.Request):
    data = await req.json()
    
    base = data.get("base")
    round_to = data.get("roundTo")
    aspectW = data.get("aspectW")
    aspectH = data.get("aspectH")

    width, height = calc_resolution(base, round_to, aspectW, aspectH)
    
    body = json.dumps({
        "width": width, 
        "height": height
    })
    return web.Response(body=body)


@endpoint.post("aspect_ratios/preset")
async def endpoint_preset_on_changed(req: web.Request):
    data = await req.json()

    preset = data.get("preset")
    
    if preset == "none":
        aspectW, aspectH = None, None
    else:
        ratio_part = preset.split("]")[-1].strip()
        aspectW, aspectH = map(int, ratio_part.split(":"))
    
    body = json.dumps({
        "aspectW": aspectW, 
        "aspectH": aspectH
    })
    return web.Response(body=body)



# ===============================================
# 短辺サイズを指定できるやつ
# ===============================================
class AspectRatiosShort:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "short": Field.int(default=800, min=0), 
                "step": Field.int(default=100, min=1), 
                "aspectW": Field.int(default=1, min=1), 
                "aspectH": Field.int(default=1, min=1), 
                "preset": Field.combo(choices=ASPECT_RATIOS_PRESETS), 
                "batch_size": Field.int(default=1, min=1), 
            }
        }
    
    RETURN_TYPES = (IO.INT, IO.INT, IO.LATENT)
    RETURN_NAMES = ("width", "height", "latent")
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, short, step, aspectW, aspectH, preset, batch_size):
        width, height = calc_resolution_short(short, step, aspectW, aspectH)
        
        latent = EmptyLatentImage().generate(width, height, batch_size)[0]
        
        return (width, height, latent)


def calc_resolution_short(short, step, aspectW, aspectH):
    if aspectW <= aspectH:
        width = short
        height = round((width * aspectH / aspectW) / step) * step
    else:
        height = short
        width = round((height * aspectW / aspectH) / step) * step

    return width, height



# endpoint
@endpoint.post("aspect_ratios_short/calc")
async def endpoint_calc_resolution(req: web.Request):
    data = await req.json()
    
    short = data.get("short")
    step = data.get("step")
    aspectW = data.get("aspectW")
    aspectH = data.get("aspectH")

    width, height = calc_resolution_short(short, step, aspectW, aspectH)
    
    body = json.dumps({
        "width": width, 
        "height": height
    })
    return web.Response(body=body)

