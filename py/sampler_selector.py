from comfy.samplers import KSampler
from .fields import Field
from .utils import category

class SamplerSelector:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sampler": Field.combo(choices=KSampler.SAMPLERS), 
                "scheduler": Field.combo(choices=KSampler.SCHEDULERS), 
            }
        }
    
    RETURN_TYPES = (KSampler.SAMPLERS, )
    RETURN_NAMES = ("sampler_name", "scheduler_name")
    CATEGORY = category
    FUNCTION = "execute"
    
    def execute(self, sampler, scheduler):
        return (sampler, scheduler)



