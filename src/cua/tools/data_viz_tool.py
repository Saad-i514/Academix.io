import os
import uuid
import sys
import tempfile
import subprocess
import glob
import shutil
from pathlib import Path
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class DataVizInput(BaseModel):
    """Input schema for DataVizTool."""
    code: str = Field(
        ..., 
        description="Python code that uses matplotlib or seaborn to generate plots. "
                    "Make sure to call plt.savefig(...) with a generic filename "
                    "like 'plot.png' or 'chart.png' in the code. The tool will capture any .png generated."
    )


class DataVizTool(BaseTool):
    name: str = "DataVizTool"
    description: str = (
        "Executes Python data visualization scripts (using matplotlib/seaborn). "
        "Any generated .png images are captured, saved to the server's uploads folder, "
        "and returned as Markdown image links for direct embedding into reports."
    )
    args_schema: type[BaseModel] = DataVizInput

    def _run(self, code: str) -> str:
        # Prepend backend configuration to prevent GUI popups
        preamble = (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "sns.set_theme(style='darkgrid')\n" # nice default theme
        )
        full_code = preamble + code

        uploads_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads")))
        uploads_dir.mkdir(parents=True, exist_ok=True)

        result_markdown = ""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "plot_script.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            try:
                result = subprocess.run(
                    [sys.executable, file_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=60,
                    cwd=temp_dir
                )
            except subprocess.TimeoutExpired:
                return "Execution timed out after 60 seconds. Code too slow or hanging."
            except Exception as e:
                return f"Execution error: {str(e)}"

            if result.returncode != 0:
                return f"Script execution failed:\n```\n{result.stderr}\n```\nStdout: {result.stdout}"

            # Look for any .png generated
            png_files = glob.glob(os.path.join(temp_dir, "*.png"))
            if not png_files:
                return f"Execution finished successfully, but no .png files were generated. Make sure your code contains `plt.savefig('filename.png')`.\nOutput: {result.stdout}"

            markdown_images = []
            for png_file in png_files:
                unique_filename = f"viz_{uuid.uuid4().hex[:8]}.png"
                dest_path = uploads_dir / unique_filename
                shutil.copy2(png_file, dest_path)
                # Use environment variable for base URL, fallback to relative path
                api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
                markdown_images.append(f"![Data Visualization]({api_base}/uploads/{unique_filename})")

            result_markdown = "\n\n".join(markdown_images)
            
            if result.stdout.strip():
                result_markdown = f"Text Output:\n```\n{result.stdout.strip()}\n```\nGenerated plots:\n{result_markdown}"
        
        return result_markdown
