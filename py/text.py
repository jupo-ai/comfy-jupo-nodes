from comfy.comfy_types import IO
from .fields import Field
from .utils import category, endpoint

class JoinStrings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "text": Field.string(forceInput=True)
            }
        }
    
    RETURN_TYPES = (IO.STRING, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, **kwargs):
        
        strings = []
        for text in kwargs.values():
            for tag in text.split(","):
                if tag.strip():
                    strings.append(tag.strip())
        
        joined = ", ".join(strings)

        return (joined, )


