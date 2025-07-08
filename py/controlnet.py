from comfy.comfy_types import IO
from .fields import Field
from .utils import category, endpoint

class RemoveControlnet:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": Field.conditioning(), 
                "negative": Field.conditioning(), 
            }
        }
    
    RETURN_TYPES = (IO.CONDITIONING, IO.CONDITIONING)
    RETURN_NAMES = ("positive", "negative")
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, positive, negative):
        def remove_cn(cond):
            c = []
            for t in cond:
                n = [t[0], t[1].copy()]

                if "control" in n[1]:
                    del n[1]["control"]
                if "control_apply_to_uncond" in n[1]:
                    del n[1]["control_apply_to_uncond"]
                c.append(n)

            return c
        
        pos = remove_cn(positive)
        neg = remove_cn(negative)
        return (pos, neg)
    
    
            