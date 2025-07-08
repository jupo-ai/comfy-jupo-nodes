from .py.utils import _name, _dname
from .py import save
from .py import latent
from .py import literals
from .py import text
from .py import controlnet
from .py import image
from .py import ranbooru
from .py import wan

NODE_CLASS_MAPPINGS = {
    _name("Save_Checkpoint"): save.SaveCheckpoint, 
    _name("Aspect_Ratios"): latent.AspectRatios, 
    _name("Int"): literals.ConstantInt, 
    _name("Float"): literals.ConstantFloat, 
    _name("Number_Convert"): literals.NumberConvert, 
    _name("String"): literals.ConstantString, 
    _name("String_Multiline"): literals.ConstantStringMultiline, 
    _name("Join_Strings"): text.JoinStrings, 
    _name("Remove_Controlnet"): controlnet.RemoveControlnet, 
    _name("Image_Flip"): image.ImageFlip, 
    _name("Perfect Pixel"): image.PerfectPixel, 
    _name("Get_Image_Side"): image.GetImageSide, 
    _name("Pixel_Resize_for_Wan"): image.PixelResizeForWan, 
    _name("Images_Sample_Evenly"): image.ImagesSampleEvenly, 
    _name("Ranbooru"): ranbooru.Ranbooru, 
    _name("WAN_LoRA_Join"): wan.WanLoraJoin, 
}

NODE_DISPLAY_NAME_MAPPINGS = {k: _dname(k) for k in NODE_CLASS_MAPPINGS}
WEB_DIRECTORY = "./web"

