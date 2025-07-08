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
    "[landscape] 7:4", 
    "[landscape] 19:13", 
    "[landscape] 3:2", 
    "[landscape] 7:5", 
    "[landscape] 9:7", 
    "[landscape] 4:3", 
    "[square] 1:1", 
    "[portrait] 3:4", 
    "[portrait] 7:9", 
    "[portrait] 5:7", 
    "[portrait] 2:3", 
    "[portrait] 13:19", 
    "[portrait] 4:7", 
    "[portrait] 1:3", 
]



class AspectRatios:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base": Field.int(default=512, min=64, step=64), 
                "fixed_side": Field.combo(["none", "short", "long"]), 
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

    def execute(self, base, fixed_side, aspectW, aspectH, preset, batch_size):
        width, height = calc_resolution(base, fixed_side, aspectW, aspectH)
        latent = EmptyLatentImage().generate(width, height, batch_size)[0]
        
        return (width, height, latent)


# javasript側で同じ計算をするため計算用関数を分離
def calc_resolution(base, fixed_side, aspectW, aspectH):
    step = 16
    aspect_ratio = aspectW / aspectH

    if fixed_side == "none":
        area = base ** 2
        width = math.sqrt(area * aspect_ratio)
        height = width / aspect_ratio

    else:
        is_short = (fixed_side == "short")
        is_portrait = aspectW <= aspectH

        if (is_short and is_portrait) or (not is_short and not is_portrait):
            width = base
            height = base * aspectH / aspectW
        else:
            height = base
            width = base * aspectW / aspectH

    # stepで丸める
    width = int(width // step * step)
    height = int(height // step * step)

    return width, height


# endpoint
@endpoint.post("aspect_ratios/calc")
async def endpoint_calc_resolution(req: web.Request):
    data = await req.json()
    
    base = data.get("base")
    fixed_side = data.get("fixedSide")
    aspectW = data.get("aspectW")
    aspectH = data.get("aspectH")

    width, height = calc_resolution(base, fixed_side, aspectW, aspectH)
    
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

