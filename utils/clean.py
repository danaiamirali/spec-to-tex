import regex as re

def clean_doc(doc: str) -> str:
    """
    Clean a provided document up by catching any programmatic errors.
    """
    # Case 1: Double \end{document} tags
    # Only retain the last \end{document} tag
    if doc.count(r'\end{document}') > 1:
        doc = re.sub(r'\\end\{document\}', '', doc)
        doc += r'\end{document}'

    # Case 2: Double \begin{document} tags
    # Only retain the first \begin{document} tag
    tags = re.findall(r'\\begin\{document\}', doc)

    if len(tags) > 1:
        # get idx of first \begin{document}
        idx = doc.index(tags[0])
        # get rid of all the tags
        doc = re.sub(r'\\begin\{document\}', '', doc)
        # add back the first tag
        doc = doc[:idx] + tags[0] + doc[idx:]

    # Case 3: Not escaping special characters
    # Escape ampersands not already escaped
    doc = re.sub(r'(?<!\\) &', ' \&', doc)

    return doc