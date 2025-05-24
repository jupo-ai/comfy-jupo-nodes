from .py.utils import _name, _dname
from .py import save
from .py import latent
from .py import literals
from .py import text

NODE_CLASS_MAPPINGS = {
    _name("Save_Checkpoint"): save.SaveCheckpoint, 
    _name("Aspect_Ratios"): latent.AspectRatios, 
    _name("Aspect_Ratios_Short"): latent.AspectRatiosShort, 
    _name("Int"): literals.ConstantInt, 
    _name("Float"): literals.ConstantFloat, 
    _name("Number_Convert"): literals.NumberConvert, 
    _name("String"): literals.ConstantString, 
    _name("String_Multiline"): literals.ConstantStringMultiline, 
    _name("Join_Strings"): text.JoinStrings, 
}

NODE_DISPLAY_NAME_MAPPINGS = {k: _dname(k) for k in NODE_CLASS_MAPPINGS}
WEB_DIRECTORY = "./web"

