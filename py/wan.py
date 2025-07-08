from .fields import Field
from .utils import log, category, endpoint

"""
kijai Wan Wrapper用
"""

class WanLoraJoin:
    @classmethod
    def INPUT_TYPES(cls):
        num = 10
        return {
            "optional": {
                **{f"lora{i}": ("WANVIDLORA", {}) for i in range(1, num+1)}
            }
        }
    
    RETURN_TYPES = ("WANVIDLORA", )
    RETURN_NAMES = ("lora", )
    CATEGORY = category
    FUNCTION = "execute"
    
    def execute(self, **kwargs):
        loras = []
        for lora_list in kwargs.values():
            if isinstance(lora_list, list):
                for lora in lora_list:
                    loras.append(lora)
        
        return (loras, )