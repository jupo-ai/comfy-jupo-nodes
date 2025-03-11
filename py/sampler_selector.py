from comfy.samplers import KSampler
from .fields import Field
from .utils import category

class SamplerSelector:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sampler": Field.combo(choices=KSampler.SAMPLERS)
            }
        }
    
    RETURN_TYPES = (KSampler.SAMPLERS, )
    RETURN_NAMES = ("sampler_name", )
    CATEGORY = category
    FUNCTION = "execute"
    
    def execute(self, sampler):
        return (sampler, )


class SchedulerSelector:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scheduler": Field.combo(choices=KSampler.SCHEDULERS)
            }
        }
    
    RETURN_TYPES = (KSampler.SCHEDULERS, )
    RETURN_NAMES = ("scheduler_name", )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, scheduler):
        return (scheduler, )

