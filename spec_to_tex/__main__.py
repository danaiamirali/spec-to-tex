import argparse
import base64
import shutil
from pdf2image import convert_from_path
from dotenv import load_dotenv
import os

"""
Given one specification file, which may be a homework assignment, project spec, etc.

We convert the specification to a LaTeX template.

We assume there are places in the specification that are meant to be filled in by the user.
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="run.py", description="Convert a specification to a LaTeX template.")
    parser.add_argument("path", help="The path to the specification file.")
    parser.add_argument("-m", "--mode", 
                        help="The mode to use for conversion. Options are 'openai', 'llama', and 'structure'. openai uses GPT4V, llama uses LlamaParse, and structure uses a pipeline of OCR and vision transformer image layout analysis to programatically build the TeX.", 
                        default="openai",
                        choices=["openai", "llama", "structure"])
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true", default=False)
    parser.add_argument("-oa", "--openai", help="The OpenAI API key to use. If not provided, we assume it is stored as an environment variable.", default=None)
    parser.add_argument("--clear-cache", help="Clear the cache of API responses.", action="store_true", default=False)
    # parser.add_argument("-p", "--precise", help="For OpenAI mode: use significantly more API calls to get more precise results. Use when normal output is inadequate or incorrect.", 
    #                     action="store_true", default=False)

    args = parser.parse_args()

    if args.openai is None:
        load_dotenv()
        API_KEY = os.getenv("OPENAI_API_KEY")
    else:
        API_KEY = args.api_key

    os.environ["OPENAI_API_KEY"] = API_KEY

    if args.clear_cache:
        from utils.cache import clear_cache
        clear_cache()

    try:
        images = convert_from_path(args.path)
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        for i, image in enumerate(images):
                image.save(f"tmp/image_{i}.jpg", "JPEG")
        if args.verbose:
            print(f"Found {len(images)} pages in the PDF.")
    except:
        print(f"Error opening file at path {args.path}.")
        exit(1)

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    encoded_images = [encode_image(os.path.join("tmp", image)) for image in os.listdir("tmp")]
    shutil.rmtree("tmp")

    # generate the latex
    if args.mode == "openai":
        from spec_to_tex.conversion import from_openai
        generated_tex: str = from_openai(encoded_images, verbose=args.verbose)
    elif args.mode == "llama":
        # from spec_to_tex.conversion import from_llama
        # generated_tex: str = from_llama(encoded_images)
        raise NotImplementedError("The 'llama' mode is not yet implemented.")
    else:
        raise NotImplementedError("The 'structure' mode is not yet implemented.")

    # save the tex
    with open("output.tex", "w") as f:
        f.write(generated_tex)

    ####
