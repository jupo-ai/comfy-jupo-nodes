from comfy.comfy_types import IO
from .fields import Field
from .utils import category, endpoint

class JoinStrings:
    @classmethod
    def INPUT_TYPES(cls):
        num = 10
        return {
            "optional": {
                **{f"text{i}": Field.string(forceInput=True) for i in range(1, num+1)}, 
            }, 
            "required": {
                "separator": Field.combo([", ", "\\n"])
            }
        }
    
    RETURN_TYPES = (IO.STRING, )
    CATEGORY = category
    FUNCTION = "execute"

    def execute(self, **kwargs):
        all_text = []
        for key, text in kwargs.items():
            if isinstance(text, str) and key != "separator":
                text = text.strip()
                text = text.rstrip(",")
                if text:
                    all_text.append(text)
        
        separator = kwargs.get("separator", "\\n")
        if separator == "\\n":
            separator = ", \n"
        joined = separator.join(all_text)

        return (joined, )


