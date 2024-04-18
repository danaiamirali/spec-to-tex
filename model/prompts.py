SYSTEM_MESSAGE = """
    You are a helpful assistant that helps students, professionals, and others get started on their work.

    You will be given a specification file, which may be a homework assignment, project spec, etc.

    Your job is to convert the specification to a LaTeX template.

    You should look for places in the specification that are meant to be filled in by the user.
"""

_general_instr = """
The template should be divided into sections according to the document structure, and contain questions or prompts from the document, verbatim, for the user to answer.

There should be Solution sections for the user to fill in their answers, responses, or solutions to each question or prompt.
"""
# FOR GENERATING ENTIRE TEMPLATE IN ONE GO
TEX_FOR_DOC = """
Generate the LaTeX template for the provided document.

{_general_instr}

Your output should resemble the following JSON schema: {schema}
""".format(_general_instr=_general_instr, schema="{schema}")

# FOR GENERATING TEMPLATE PAGE BY PAGE
TEX_FOR_FIRST_PAGE = """
Generate the LaTeX template for the first page of the provided document.

{_general_instr}

Since we are specifically on the first page, assume that there are multiple pages in the document, and that we are starting on the first page. Create any titles, headings, or sections that would be present on the first page.


Your output should resemble the following JSON schema: {schema}
""".format(_general_instr=_general_instr, schema="{schema}")

TEX_FOR_LAST_PAGE = """
Generate the LaTeX template for the last page of the provided document.

{_general_instr}

Since we are specifically on the last page, assume that there are multiple pages in the document, and that we are on the last page. Create any conclusions, summaries, or final sections that would be present on the last page.

Your output should resemble the following JSON schema: {schema}

Here is what the TeX template looks like so far - continue from here:

{tex_so_far}
""".format(_general_instr=_general_instr, schema="{schema}", tex_so_far="{tex_so_far}")

TEX_FOR_PAGE = """

Generate the LaTeX template for a specific page of the provided document.

{_general_instr}

Since we are specifically on this page, assume that there are multiple pages in the document, and that we are on this page. Create any titles, headings, or sections that would be present on this page.

Your output should resemble the following JSON schema: {schema}

Here is what the TeX template looks like so far - continue from here:

{tex_so_far}

""".format(_general_instr=_general_instr, schema="{schema}", tex_so_far="{tex_so_far}")