# spec-to-tex
Using GPT-4V to generate LaTeX templates for problem sets or writeups based on a homework assignment or spec.

The program is currently a CLI tool.

## Usage
```sh
python3 cli.py {path-to-file-to-convert} {command-line args}
```

The command line args are as follows:

- `mode`: takes one of `openai`, `llama`, `structure`. Currently only `openai` is implemented; selecting `openai` will lead to the program using GPT4V to perform the conversion. `llama` will use LlamaParse and `structure` will use a pipeline of OCR and Document Image Layout Transformers to programatically create the LaTeX template. Contributions would be appreciated. Ex: `--mode="openai"`
- `openai`: use to set API key for GPT4V. Ex: `--openai="{key}"`
- `verbose`: use to indicate verbosity of output. Ex: `-v`
- `clear-cache`: use to clear the cache before performing the TeX conversion. (OpenAI responses are cached to reduce API calls)

Example for using OpenAI:
```sh
python3 cli.py documents/hw.pdf --mode="openai" --openai="sk102031" --verbose
```
