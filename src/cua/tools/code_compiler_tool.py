from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import tempfile
import subprocess


class CodeCompilerInput(BaseModel):
    """Input schema for CodeCompilerTool."""
    code: str = Field(..., description="The code to compile.")
    language: str = Field(..., description="The programming language.")


def run_code(code: str, language: str = "python") -> str:
    language = (language or "python").strip().lower()

    with tempfile.TemporaryDirectory() as temp_dir:
        if language == "python":
            file_path = os.path.join(temp_dir, "temp.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = ["python", file_path]

        elif language == "c":
            file_path = os.path.join(temp_dir, "temp.c")
            exe_path = os.path.join(temp_dir, "temp.exe")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(["gcc", file_path, "-o", exe_path], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return compile_result.stderr or "Compilation failed with no stderr output."

            cmd = [exe_path]

        elif language == "java":
            import re
            # Try to find 'public class Name' to name the file correctly
            match = re.search(r"public\s+class\s+(\w+)", code)
            class_name = match.group(1) if match else "Main"
            
            file_path = os.path.join(temp_dir, f"{class_name}.java")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
 
            compile_result = subprocess.run(["javac", file_path], capture_output=True, text=True, cwd=temp_dir)
            if compile_result.returncode != 0:
                return compile_result.stderr or "Compilation failed with no stderr output."
 
            cmd = ["java", "-cp", temp_dir, class_name]

        else:
            return f"Unsupported language: {language}. Supported languages are python, c, and java."

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            return "Execution timed out after 15 seconds."
        except FileNotFoundError as e:
            return f"Compiler/interpreter not found: {e}. Please ensure {language} is installed."
        except Exception as e:
            return f"Execution error: {str(e)}"

        if result.returncode != 0:
            return result.stderr or "Execution failed with no stderr output."
        return result.stdout or "Execution finished with no output."


class CodeCompilerTool(BaseTool):
    name: str = "CodeCompilerTool"
    description: str = "Compiles and executes code in a specified programming language."
    args_schema: type[BaseModel] = CodeCompilerInput

    def _run(self, code: str, language: str) -> str:
        return run_code(code, language)