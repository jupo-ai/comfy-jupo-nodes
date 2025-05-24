from comfy.comfy_types import IO
from .fields import Field
from .utils import log, category, endpoint


class ConstantInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": Field.int()
            }
        }
    
    RETURN_TYPES = (IO.INT, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, value):
        return (value, )


class ConstantFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": Field.float(step=0.001)
            }
        }
    
    RETURN_TYPES = (IO.FLOAT, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, value):
        return (value, )


class NumberConvert:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": Field.number()
            }
        }
    
    RETURN_TYPES = (IO.INT, IO.FLOAT, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, value):
        return (int(value), float(value))


class ConstantString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": Field.string()
            }
        }
        
    RETURN_TYPES = (IO.STRING, )
    CATEGORY = category
    FUNCTION = "execute"
    
    def execute(self, text): 
        return (text, )


class ConstantStringMultiline:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": Field.string(multiline=True)
            }
        }
    
    RETURN_TYPES = (IO.STRING, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, text): 
        return (text, )


