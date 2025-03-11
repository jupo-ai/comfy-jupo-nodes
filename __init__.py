from .py.utils import _name, _dname
from .py import save
from .py import aspect_ratios
from .py import sampler_selector

NODE_CLASS_MAPPINGS = {
    _name("Save_Checkpoint"): save.SaveCheckpoint, 
    _name("Aspect_Ratios"): aspect_ratios.AspectRatios, 
    _name("Sampler_Selector"): sampler_selector.SamplerSelector, 
    _name("Scheduler_Selector"): sampler_selector.SchedulerSelector, 
}

NODE_DISPLAY_NAME_MAPPINGS = {k: _dname(k) for k in NODE_CLASS_MAPPINGS}
WEB_DIRECTORY = "./web"

