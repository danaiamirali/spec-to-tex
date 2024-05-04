import json
import requests
from ..prompts import SYSTEM_MESSAGE

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

def get_response(api_key: str, prompt: str, images: list | None = None) -> dict:
    headers, payload = _get_headers_and_payload(api_key, prompt, images)
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()