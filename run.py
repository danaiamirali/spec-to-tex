import argparse
from pdf2image import convert_from_path
import base64
from dotenv import load_dotenv
import os
from PIL import Image

"""
Given one specification file, which may be a homework assignment, project spec, etc.

We convert the specification to a LaTeX template.

We assume there are places in the specification that are meant to be filled in by the user.
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="run.py", description="Convert a specification to a LaTeX template.")
    parser.add_argument("path", help="The path to the specification file.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true", default=False)
    parser.add_argument("-k", "--api-key", help="The OpenAI API key to use.", default=None)
    parser.add_argument("-p", "--precise", help="Use significantly more API calls to get more precise results. Use when normal output is inadequate or incorrect.", 
                        action="store_true", default=False)

    args = parser.parse_args()

    if args.api_key is None:
        load_dotenv()
        API_KEY = os.getenv("OPENAI_API_KEY")
    else:
        API_KEY = args.api_key

    try:
        images = convert_from_path(args.path)
        if args.verbose:
            print(f"Found {len(images)} images in the PDF.")
            for i, image in enumerate(images):
                image.save(f"image_{i}.jpg", "JPEG")
            print("Images saved to disk.")
    except:
        print(f"Error opening file at path {args.path}.")
        exit(1)

    def encode_image(image: Image):
        return base64.b64encode(Image).decode('utf-8')
    
    images = [encode_image(image) for image in images]

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
    }


    if args.precise:
        # Use more API calls to get more precise results
        # Generate one page at a time, and generate multiple completions for each page
        # Have the model rank the completions and pick the best one
        pass
    else:
        # Use fewer API calls to get faster results
        # Generate all completions at once
        pass

    ####

    SYSTEM_MESSAGE = """

        {fancy prompt about converting images to text}

    """

    payload = {
    "model": "gpt-4-turbo",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "What’s in this image?"
            },
        ]
        }
    ],
    "max_tokens": 300
    }

    for image in images:
        payload["messages"][0]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                }
            }
        )
    
