"""
Main code for the conversion of a specification document to a LaTeX template.

Draws on abstractions defined in other modules to form a pipeline for the conversion process.

"""

from pydantic import BaseModel, Field, ValidationError
from utils.clean import clean_doc
import os

SYSTEM_MESSAGE = """
    You have been given a specification document, which can either be a homework assignment, project spec, etc. 
    This document is provided in the form of images.
    Your task is to convert the specification to a LaTeX template.
    The LaTeX template should contain everything from the specification document that could be useful for the user or useful to answering any questions or prompts provided in the document. This includes text, tables, equations, etc.
    If there are any parts of the document that are meant to be filled in by the user, please leave those parts blank in the LaTeX template and prompt the user to fill them in by providing an explicit prompt.
"""

def from_openai(images: list[int], verbose: bool = False, retries_limit: int = 3) -> str:
    """
    Given a list of encoded images (of a document), return a LaTeX template for the document.
    """
    from spec_to_tex.wrappers.openai import Client

    api_key = os.getenv("OPENAI_API_KEY")

    # First, we generate the LaTeX template for the document.
    # 1. Define a Pydantic model for the LaTeX document.
    # 2. Generate the LaTeX template with GPT-4V.
    class TeXDocument(BaseModel):
        packages_needed: list[str] = Field(... , description="The packages to be used in the LaTeX document. For example, 'amsmath', 'graphicx', etc. List them here, and they will be included in the LaTeX document.")
        document_body:   str = Field(..., description="The body of the LaTeX document. Assume this is wrapped in the document environment (so there is no need to open or close the environment), and that imports, document class definition, and anything else that would be in the header is in the header.")

        def __str__(self) -> str:
            return """
            \\documentclass[11pt,addpoints]{exam}
            """ + "\n".join(
            ["\\usepackage{package}".format(package="{" + package + "}") for package in self.packages_needed]
            ) + """
            \\begin{document}
            {body}
            \\end{document}            
            """.format(body=self.document_body, document="{document}")

    prompt = r"""
        Generate the LaTeX template for the specification document provided in the images.

        Make sure your generated LaTeX template will correctly render and compile. In particular, avoid issues with:
        - Missing packages
        - Incorrectly formatted LaTeX code
            - Ampersands (&) in text not being escaped
               - Not escaping special characters in general
            - Not closing environments properly
        
        Sample LaTeX template:

        \begin{questions}
        \question \textbf{Short-answer potpourri.}
        
        \begin{parts}
            \part[5] Suppose that Alice's bit string (a binary number) is $x=100000100$ and Bob's bit string is $y=10010001$.
            List, with justification, all the ``bad'' primes~$p$ for which the fingerprinting protocol from class will \emph{fail} to detect that $x\neq y$.
            (Recall that $x$ and $y$ are interpreted as integers written in base two, with digits written from most to least significant.)
            
            \begin{solution}

            \end{solution}

            \part[5] In class we saw that 2 is not a generator of $\mathbb{Z}_7^*$, but 3 is. State, with justification, all the other elements of $\mathbb{Z}_7^*$ that are generators of $\mathbb{Z}_7^*$.

            \begin{solution}
                
            \end{solution}

            \part[5] \emph{This part relies on material from the lecture on 4/15.}
            
            On the distant planet of Arrakis, every month has exactly 35 days (numbered from zero).
            The Bene Gesserit's plans are measured in \emph{centuries}.
            One month, on the $0$th day, they set a plan in motion that, exactly $3^{28}$ days later, will finally defeat the tyrannical Emperor Leto (the son of the Kwisatz Haderach, of course).
            Determine the day of the month when this will occur.
            Do not use any electronic computations, use as little by-hand calculation as you can, and show your work.

            \begin{solution}
                
            \end{solution}

            \part[5] \emph{This question relies on material from the lecture on 4/17.}
            
            Pam shows Creed two pictures and claims that they are different, but Creed cannot see any difference between them.
            Pam wants to convince Creed that they really are different, but without revealing what the difference is.
            How can Creed test Pam so that if the pictures really are different, Pam will pass the test while revealing nothing more than this fact to Creed; and if the pictures are identical, Pam will fail the test with probability at least~99\%?
            (Just describe the test; you do not need to prove any of its properties.)

            \begin{solution}
                
            \end{solution}
        \end{parts}
        \pagebreak

        \end{questions}

        Generated LaTeX template:
    """

    if verbose:
        print("Generating the LaTeX template for the document...")

    generator = Client(api_key, schema=TeXDocument, system_message=SYSTEM_MESSAGE)
    response: dict = generator.get_response(prompt, system_message=SYSTEM_MESSAGE, images=images)
    print(response)
    document: TeXDocument = TeXDocument(**response)

    if verbose:
        print("Generated the LaTeX template for the document.")
        print(document)

    # Next, we analyze the LaTeX document to ensure it will render and compile correctly.
    # 1. Define a Pydantic model for the LaTeX document. We will structure the model to help the model develop a chain of thought, but will only use the document_body field.
    # 2. Generate the analysis of the LaTeX document with GPT-4V.
    # 3. If the document will not render and compile correctly, generate a fix for the document with GPT-4V.

    if verbose: 
        print("Analyzing the LaTeX document...")

    class Analysis(BaseModel):
        analysis: str = Field(default="There seem to be no problems. The provided LaTeX document will render and compile correctly.", description="The analysis of errors with the LaTeX document.")
        will_render: bool = Field(default=True, description="Whether the LaTeX document will render and compile correctly.")

        def __str__(self) -> str:
            return self.analysis

    analyzer = Client(api_key, schema=Analysis, system_message=SYSTEM_MESSAGE)

    prompt = f"""
        Analyze the provided LaTeX document. Will it correctly render and compile? 
        In particular, ensure that:
        - All special characters are escaped
        - All environments are closed properly
            - Tags are not double-closed or opened
        - All packages needed are included
        - Non-existent packages are not included

        Document:

        {document}
    """

    response: dict = analyzer.get_response(prompt, system_message=SYSTEM_MESSAGE)
    analysis: Analysis = Analysis(**response)

    # If the document will not render and compile correctly, generate a fix for the document.
    num_retries = 0
    while not analysis.will_render:

        if verbose:
            print("The provided LaTeX document will not render and compile correctly.")
            print("The analysis of the document is as follows:")
            print(analysis)
            print()
            print("Generating a fix for the document...")

        class Fix(BaseModel):
            fix: str = Field(description="The corrected LaTeX document, which will compile and render correctly.")

        fixer = Client(api_key, schema=Fix, system_message=SYSTEM_MESSAGE)

        prompt = f"""
            Given the below LaTeX document and an analysis of some issues with the document, provide a fix for the document.

            Ensure that your fix will allow the document to render and compile correctly.

            Document:

            {document}

            Analysis:

            {analysis}

            Fixed Document:
        """
        response: dict = fixer.get_response(prompt, system_message=SYSTEM_MESSAGE)
        fix: Fix = Fix(**response)

        document.document_body = fix.fix
        if verbose:
            print("Generated a fix.")
        num_retries += 1

        if num_retries >= retries_limit:
            if verbose:
                print("Reached the maximum number of retries. Breaking...")
            break
        else:
            # re-analyze the document to ensure it will render and compile correctly.
            if verbose:
                print("Re-analyzing the document...")
            response: dict = analyzer.get_response(prompt, system_message=SYSTEM_MESSAGE)
            analysis: Analysis = Analysis(**response)

    if num_retries < retries_limit:
        print("TeX creation successful.")
    else:
        print("TeX has been created. However, there may be issues with the document.")

    return clean_doc(document.__str__().strip())

def from_llama(path: str) -> str:
    from spec_to_tex.wrappers.llamaparse import get_response

    prompt = """
        Recreate the provided document, but in LaTeX.

        If there are any parts of the document that are meant to be filled in by the user, please leave those parts blank in the LaTeX template and prompt the user to fill them in by providing an explicit prompt.
    """

    response: str = get_response(prompt, path)
    print(response)

    return response