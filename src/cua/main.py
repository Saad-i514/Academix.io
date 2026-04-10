#!/usr/bin/env python
import re
import sys
import os
import warnings
from datetime import datetime

from cua.crew import Cua
from cua.memory import generate_notes_with_memory, save_chat, save_note, save_report, close_memory

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information.

DEFAULT_USER_INPUT = os.getenv("USER_INPUT", "").strip()


def _extract_youtube_url(text: str) -> str:
    match = re.search(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+)", text)
    return match.group(0) if match else ""


def _extract_code_block(text: str) -> tuple[str, str]:
    """Extract a fenced code block and language from user input."""
    pattern = r"```(?P<lang>[a-zA-Z0-9_+-]*)[ \t]*\r?\n(?P<code>[\s\S]*?)```"
    match = re.search(pattern, text)
    if not match:
        return "", "python"

    language = (match.group("lang") or "python").strip().lower()
    code = match.group("code").strip()
    return code, language or "python"


def _extract_lab_manual_path(text: str) -> str:
    """Extract a file path from user input (e.g., c:/path/to/manual.md)."""
    # Look for common file extensions in paths
    match = re.search(r"[a-zA-Z]:[\\\/\w\d._ -]+\.(?:pdf|md|docx|txt)", text)
    return match.group(0) if match else ""


def _detect_youtube_output_mode(user_input: str) -> str:
    lowered = user_input.lower()

    transcript_keywords = (
        "transcript only",
        "just transcript",
        "raw transcript",
        "full transcript",
        "no summary",
        "without summary",
        "don't summarize",
        "do not summarize",
        "skip summary",
    )
    if any(keyword in lowered for keyword in transcript_keywords):
        return "transcript"

    return "summary"


def _build_inputs(user_input: str):
    youtube_url = _extract_youtube_url(user_input)
    code, language = _extract_code_block(user_input)
    lab_manual_path = _extract_lab_manual_path(user_input)
    youtube_output_mode = _detect_youtube_output_mode(user_input)

    topic = "General Topic" if youtube_url else user_input
    memory_context = generate_notes_with_memory(user_input)

    return {
        "topic": topic,
        "youtube_url": youtube_url,
        "user_input": user_input,
        "memory_context": memory_context,
        "task_type": "AUTO",
        "code": code,
        "language": language,
        "lab_manual_path": lab_manual_path,
        "youtube_output_mode": youtube_output_mode,
        "planner_goal": "Dynamically choose the best workflow and tools from the user_input.",
        "current_year": str(datetime.now().year),
    }


def _output_path_for_result() -> str:
    return "report.md"


def run():
    """
    Run the crew.
    """
    if not DEFAULT_USER_INPUT:
        # Fallback to command line arguments if any
        if len(sys.argv) > 1:
            user_input = " ".join(sys.argv[1:])
        else:
            print("Error: USER_INPUT environment variable is empty and no command line arguments provided.")
            print("Please set USER_INPUT in your .env file or provide input as arguments.")
            print("Example: python -m cua.main \"Summarize this video: https://youtube.com/...\"")
            sys.exit(1)
    else:
        user_input = DEFAULT_USER_INPUT
    
    inputs = _build_inputs(user_input)

    try:
        result = Cua().crew(inputs=inputs).kickoff(inputs=inputs)
        result_text = str(result)
        save_chat(inputs["user_input"], result_text)

        report_text = (
            f"# CUA Result\n\n"
            f"- Request: {inputs['user_input']}\n"
            f"- Routing Mode: auto\n"
            f"- Code Language: {inputs['language']}\n\n"
            f"## Result\n\n{result_text}\n"
        )
        save_note(f"CUA - {inputs['topic']}", result_text)
        save_report(report_text, path=_output_path_for_result())
        print(f"\n✓ Results saved to {_output_path_for_result()}")
    except Exception as e:
        print(f"Error: An error occurred while running the crew: {e}")
        raise
    finally:
        close_memory()


 

 

if __name__ == "__main__":
    run()