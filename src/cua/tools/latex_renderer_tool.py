"""
LatexRendererTool — Renders LaTeX math equations as PNG images.

NO API KEY REQUIRED — uses matplotlib (already installed).

Renders equations like:
  S = \\frac{1}{(1-P) + P/N}
  \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}

Returns a Markdown image link pointing to the saved PNG.
"""

import os
import uuid
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class LatexInput(BaseModel):
    equation: str = Field(
        ...,
        description="LaTeX equation string (without $ delimiters). E.g.: S = \\\\frac{1}{(1-P) + P/N}"
    )
    label: str = Field("", description="Optional label/caption for the equation")
    fontsize: int = Field(16, description="Font size for the equation (default 16)")


class LatexRendererTool(BaseTool):
    name: str = "LatexRenderer"
    description: str = (
        "Renders a LaTeX mathematical equation as a PNG image. "
        "Returns a Markdown image link that can be embedded directly in reports. "
        "Use this for important equations in the Theory section to make them look professional."
    )
    args_schema: type[BaseModel] = LatexInput

    def _run(self, equation: str, label: str = "", fontsize: int = 16) -> str:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            return "Error: matplotlib not installed."

        uploads_dir = Path(os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../uploads")
        ))
        uploads_dir.mkdir(parents=True, exist_ok=True)

        filename = f"eq_{uuid.uuid4().hex[:8]}.png"
        dest = uploads_dir / filename

        try:
            fig, ax = plt.subplots(figsize=(8, 1.5))
            ax.axis("off")

            # Wrap in $$ for matplotlib math rendering
            display_eq = f"${equation}$"
            ax.text(
                0.5, 0.5, display_eq,
                fontsize=fontsize,
                ha="center", va="center",
                transform=ax.transAxes,
                color="#1a1a2e",
            )

            if label:
                ax.text(
                    0.5, 0.05, label,
                    fontsize=10,
                    ha="center", va="bottom",
                    transform=ax.transAxes,
                    color="#666666",
                    style="italic",
                )

            plt.tight_layout(pad=0.5)
            plt.savefig(str(dest), dpi=150, bbox_inches="tight",
                        facecolor="white", edgecolor="none")
            plt.close(fig)

            api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
            md_link = f"![{label or 'Equation'}]({api_base}/uploads/{filename})"
            return f"Equation rendered successfully.\n{md_link}"

        except Exception as e:
            plt.close("all")
            return f"Rendering failed: {e}. Equation: {equation}"
