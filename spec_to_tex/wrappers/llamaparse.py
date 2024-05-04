import nest_asyncio
nest_asyncio.apply()
from llama_parse import LlamaParse
from dotenv import load_dotenv
import regex as re

load_dotenv()

def remove_duplicate_substrings(text, substring, first=True):
    # Find all start indices of the substring in the text
    indices = [m.start() for m in re.finditer(re.escape(substring), text)]
    if not indices:
        return text  # Return the original text if the substring is not found
    
    # Keep the first occurrence and remove the rest
    if first:
        first_index = indices[0]
        return (text[:first_index + len(substring)] +
                text[first_index + len(substring):].replace(substring, ""))
    else: # last
        last_index = indices[-1]
        return (text[:last_index].replace(substring, "") +
                text[last_index:])


def get_response(prompt: str, document_path: str) -> str:
    response = LlamaParse(result_type="markdown", parsing_instruction=prompt).load_data(document_path)
    response = response[0].text

    # apply post-processing 
    # this is necessary because llamaparse treats each page as a separate document

    # get rid of every \documentclass{article} that is not the first one
    response = remove_duplicate_substrings(response, "\\documentclass{article}")

    # get rid of every \begin{document} that is not the first one
    response = remove_duplicate_substrings(response, "\\begin{document}")

    # get rid of every \end{document} that is not the last one
    response = remove_duplicate_substrings(response, "\\end{document}", first=False)

    print(response)

    return response