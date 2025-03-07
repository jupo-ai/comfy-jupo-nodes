import json
import math
from aiohttp import web
from comfy.comfy_types import IO
from .fields import Field
from .utils import log, category, endpoint


class AspectRatios:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_resolution": Field.int(default=512, min=0), 
                "round_to": Field.int(default=64, min=1), 
                "aspectW": Field.int(default=1, min=1), 
                "aspectH": Field.int(default=1, min=1), 
            }
        }
    
    RETURN_TYPES = (IO.INT, IO.INT)
    RETURN_NAMES = ("width", "height")
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, base_resolution, aspectW, aspectH):
        width, height = calc_resolution(base_resolution, aspectW, aspectH)
        
        return (width, height)



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