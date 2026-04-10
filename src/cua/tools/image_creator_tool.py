from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import base64
import zlib
import re
import textwrap

def encode_diagram(text):
    compressed = zlib.compress(text.encode("utf-8"), 9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")
 

def get_diagram_image(diagram_code, diagram_type="mermaid", fmt="png"):
    # Encode the diagram text
    encoded = encode_diagram(diagram_code)

    # Build the URL
    url = f"https://kroki.io/{diagram_type}/{fmt}/{encoded}"

    # Simply return the URL — the browser or Streamlit can fetch it
    return url


def _escape_mermaid_label(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = cleaned.replace("\\", "\\\\").replace('"', "\\\"")
    return cleaned or "Concept"


def _build_mermaid_diagram(description: str) -> str:
    fragments = [
        fragment.strip(" .;:-")
        for fragment in re.split(r"[,;]\s*|\sand\s|\swith\s", description)
        if fragment.strip()
    ]

    if not fragments:
        fragments = [description]

    root_label = _escape_mermaid_label(textwrap.shorten(description, width=60, placeholder="..."))
    child_labels = [_escape_mermaid_label(textwrap.shorten(fragment, width=34, placeholder="...")) for fragment in fragments[:4]]

    lines = ["flowchart TD", f'    A["{root_label}"]']
    for index, label in enumerate(child_labels, start=1):
        node = chr(ord("A") + index)
        lines.append(f'    {node}["{label}"]')
        lines.append(f"    A --> {node}")

    if len(child_labels) == 1:
        lines.append('    B["Visual summary"]')
        lines.append("    A --> B")

    return "\n".join(lines)


class ImageCreatorInput(BaseModel):
    """Input schema for ImageCreatorTool."""
    description: str = Field(..., description="A description of the image to create.")


class ImageCreatorTool(BaseTool):
    name: str = "ImageCreator"
    description: str = "Creates a Mermaid diagram based on a description and returns a Kroki image link."
    args_schema: type[BaseModel] = ImageCreatorInput

    def _run(self, description: str) -> str:
        mermaid_code = _build_mermaid_diagram(description)
        return get_diagram_image(mermaid_code)