from pydantic import BaseModel
from model.prompts import *
from model.schema import Output, PageOutput, DebugOutput
from model.wrappers.openai import get_response, parse_output
from utils import cache

@cache
def _generate_tex(images: list, api_key: str, precise: bool = False) -> BaseModel:
    if not precise:
        response = get_response(api_key, TEX_FOR_DOC.format(schema=Output.model_json_schema()), images=images)
        return Output(**parse_output(response))
    
    # TO DO: HAVE MODEL RANK COMPLETIONS AND PICK BEST ONE

    # precise output
    running_tex = ""
    response = get_response(api_key, TEX_FOR_FIRST_PAGE.format(schema=PageOutput.model_json_schema()), images=images[0])
    running_tex += PageOutput(response)

    for i in range(1, len(images)-1):
        response = get_response(api_key, TEX_FOR_PAGE.format(schema=PageOutput.model_json_schema(), 
                                                                tex_so_far=running_tex.__str__()), images=images[i])
        running_tex += PageOutput(response)
    
    response = get_response(api_key, TEX_FOR_LAST_PAGE.format(schema=PageOutput.model_json_schema(),
                                                                tex_so_far=running_tex.__str__()), images=images[-1])
    running_tex += PageOutput(response)

    return Output(running_tex)

def _fix_tex(tex: str, api_key: str) -> BaseModel:
    prompt = DEBUG_PROMPT.format(schema=DebugOutput.model_json_schema(), tex=tex)
    response = get_response(api_key, prompt)
    # print("Debug:", parse_output(response))
    return DebugOutput(**parse_output(response))

# Abstraction to generate LaTeX from images
class TeXGenerator():
    def __init__(self, precise=False, verbose=False):
        self.precise = precise
        self.verbose = verbose

    def __call__(self, images: list, api_key: str) -> str:
        tex: Output = _generate_tex(images, api_key, self.precise)
        if self.verbose:
            print(f"Generated LaTeX: {tex}")
        return tex.__str__()

# Abstraction to review and fix LaTeX previously generated
class TeXFixer():
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __call__(self, tex: str, api_key: str) -> str:
        tex: DebugOutput = _fix_tex(tex, api_key)
        if self.verbose:
            print(f"Is the LaTeX correct? {tex.is_correct}")
            print(f"Errors: {tex.bugs}")
            print(f"Corrected LaTeX: {tex.corrected_tex}")
        return tex.__str__()