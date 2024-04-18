from pydantic import BaseModel

# for precise output
class PageOutput(BaseModel):
    page_description: str
    does_page_need_filling: bool
    latex_for_page: str

    def __str__(self):
        return self.latex_for_page

# for general output
class Output(BaseModel):
    tex: list[PageOutput]

    def __str__(self):
        return "\n".join([str(page) for page in self.tex])

if __name__ == "__main__":
    print(Output.model_json_schema())