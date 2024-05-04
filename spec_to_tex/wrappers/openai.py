"""
Simple OpenAI API wrapper to use GPT-4V with structured output.
"""

import json
import requests
from utils.cache import lru_cache
from pydantic import BaseModel

def parse_output(response: dict) -> dict:
    try:
        output = (response['choices'][0]['message']['content'])
        output = json.loads(output)
    except Exception as e:
        print("Could not parse output from OpenAI API. Output was: ", response)
        raise e
    return output

def _get_headers_and_payload(api_key: str, prompt: str, system_message: str | None = None, images : list | None = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    system_message = {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": system_message
            }
        ]
    } if system_message else None

    payload = {
        "model": "gpt-4-turbo",
        "response_format":{"type": "json_object"},
        "messages": [

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
        "temperature": 0.0,
    } 

    idx = 0
    if system_message:
        payload["messages"].insert(0, system_message)
        idx = 1

    if images:
        for image in images:
            payload["messages"][idx]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",
                        "detail": "high"
                    }
                }
            )

    return headers, payload

@lru_cache
def get_response(api_key: str, prompt: str, system_message: str | None = None, images: list | None = None) -> dict:
    headers, payload = _get_headers_and_payload(api_key, prompt, system_message, images)
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

class Client:
    def __init__(self, api_key: str, schema: BaseModel | None = None, system_message: str | None = None):
        self.api_key = api_key
        self.schema = schema
        self.system_message = system_message
        

    def get_response(self, prompt: str, schema: BaseModel | None = None, system_message: str | None = None, images: list | None = None) -> dict:
        schema = schema if schema else self.schema
        
        if schema:
            prompt = f"""
                Respond to the following prompt with a JSON object that conforms to the following schema:
                {schema.model_json_schema()}
                Prompt: 
                {prompt}
            """
        
        return parse_output(get_response(self.api_key, prompt, system_message or self.system_message, images))