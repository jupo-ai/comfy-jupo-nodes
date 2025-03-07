from .py.utils import _name, _dname
from .py import save
from .py import aspect_ratios

NODE_CLASS_MAPPINGS = {
    _name("Save_Checkpoint"): save.SaveCheckpoint, 
    _name("Aspect_Ratios"): aspect_ratios.AspectRatios, 
}

NODE_DISPLAY_NAME_MAPPINGS = {k: _dname(k) for k in NODE_CLASS_MAPPINGS}
WEB_DIRECTORY = "./web"

