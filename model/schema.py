from pydantic import BaseModel, Field

# for precise output
class PageOutput(BaseModel):
    page_description: str = Field(..., description="Describe all the content on the page.")
    does_page_need_filling: bool = Field(..., description="Does this page contain any questions or prompts that need to be filled in by the user?")
    latex_for_page: str = Field(..., description="Generate the LaTeX template for this page, copying questions or prompts in their entirety, verbatim.")

    def __str__(self):
        return self.latex_for_page

# for general output
class Output(BaseModel):
    tex: list[PageOutput]

    def __str__(self):
        return "\n".join([str(page) for page in self.tex])
    
class DebugOutput(BaseModel):
    is_correct: bool = Field(..., description="Does the provided LaTeX have any bugs?")
    bugs: list[str] = Field(..., description="List the bugs in the LaTeX.")
    corrected_tex: str = Field(..., description="The corrected LaTeX.")

    def __str__(self):
        return self.corrected_tex

if __name__ == "__main__":
    print(Output.model_json_schema())