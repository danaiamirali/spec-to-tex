from pydantic import BaseModel
from model.prompts import *
from model.schema import Output, PageOutput
import requests
import json

def parse_output(response: dict) -> str:
    try:
        output = (response['choices'][0]['message']['content'])
        output = json.loads(output)
    except Exception as e:
        print("Could not parse output from OpenAI API. Output was: ", response)
        raise e
    return output

def _get_headers_and_payload(api_key: str, prompt: str, images: list | None = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "response_format":{"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": SYSTEM_MESSAGE
                    }
                ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                },
            ]
            }
        ],
    } 

    if images:
        for image in images:
            payload["messages"][1]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",
                        "detail": "high"
                    }
                }
            )

    return headers, payload

def _generate_tex(images: list, api_key: str, precise: bool = False) -> BaseModel:
    if not precise:
        headers, payload = _get_headers_and_payload(api_key, TEX_FOR_DOC.format(schema=Output.model_json_schema()), images)
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        print(parse_output(response.json()))
        return Output(**parse_output(response.json()))
    
    # TO DO: HAVE MODEL RANK COMPLETIONS AND PICK BEST ONE

    # precise output
    running_tex = ""
    headers, payload = _get_headers_and_payload(api_key, TEX_FOR_FIRST_PAGE.format(schema=PageOutput.model_json_schema()), images=images[0])
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    running_tex += PageOutput(response.json())

    for i in range(1, len(images)-1):
        headers, payload = _get_headers_and_payload(api_key, TEX_FOR_PAGE.format(schema=PageOutput.model_json_schema(),
                                                                                 tex_so_far=running_tex.__str__()), images=images[i])
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        running_tex += PageOutput(response.json())
    
    headers, payload = _get_headers_and_payload(api_key, TEX_FOR_LAST_PAGE.format(schema=PageOutput.model_json_schema(),
                                                                                    tex_so_far=running_tex.__str__()), images=images[-1])
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    running_tex += PageOutput(response.json())

    return Output(running_tex)



class TeXGenerator():
    def __init__(self, precise=False):
        self.precise = precise

    def __call__(self, images: list, api_key: str) -> str:
        tex: Output = _generate_tex(images, api_key, self.precise)
        return tex.__str__()

class TeXFixer():
    def __call__(self, tex: str) -> str:
        raise NotImplementedError