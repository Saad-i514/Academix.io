import os
import sys
import shutil
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv

# ── Load env from cua/.env ──────────────────────────────────────────────────
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from cua.crew import Cua
from cua.memory import save_chat, save_note, get_chat_history
from cua.tools.youtube_video_downloader_tool import MultimediaAssistantTool
from app.llm import get_llm
from app.report_exporter import markdown_to_docx

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Academix")

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Academix.io API",
    description="Academic automation engine — reports, transcription, chat.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}


# ── Chat ─────────────────────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat(
    message: str = Form(...),
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_groq_key: Optional[str] = Header(None, alias="X-Groq-Key"),
    x_serper_key: Optional[str] = Header(None, alias="X-Serper-Key"),
):
    try:
        msg_lower = message.lower()

        # Identity questions — hardcoded
        if any(q in msg_lower for q in ["who created you", "who made you", "who built you"]):
            response = (
                "I am the **Academix Agent**, created by **Muhammad Saad bin Mazhar**. "
                "I'm a production-grade academic automation assistant built to help students "
                "and researchers generate reports, transcribe lectures, and automate academic tasks."
            )
            save_chat(message, response)
            return {"response": response}

        if any(q in msg_lower for q in ["what can you do", "how can you help", "what are you"]):
            response = (
                "I can help you with:\n"
                "• **Report Creation** — Upload a lab manual or describe your assignment and I'll generate a complete report\n"
                "• **Transcription** — Paste a YouTube link or upload any audio/video to get transcription and study notes\n"
                "• **Academic Queries** — Ask me anything about your studies, research, or coursework\n\n"
                "Use the sidebar to access Report Studio or Transcription Hub for full automation!"
            )
            save_chat(message, response)
            return {"response": response}

        # Use LLM for real academic responses
        llm = get_llm(user_openai_key=x_openai_key, user_groq_key=x_groq_key)

        if llm:
            system_prompt = (
                "You are the Academix Agent, an academic AI assistant created by Muhammad Saad bin Mazhar. "
                "You ONLY answer academic and educational questions. "
                "If asked about non-academic topics, politely redirect to academic assistance. "
                "Be concise, helpful, and professional."
            )
            result = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ])
            response = result.content if hasattr(result, "content") else str(result)
        else:
            response = (
                f"I understand you're asking about '{message}'. "
                "As your Academix Agent, I'm here to help with academic tasks. "
                "For detailed report generation or transcription, use the dedicated modules in the sidebar!"
            )

        save_chat(message, response)
        return {"response": response}

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Report ────────────────────────────────────────────────────────────────────
@app.post("/api/report")
async def generate_report(
    prompt: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_groq_key: Optional[str] = Header(None, alias="X-Groq-Key"),
    x_serper_key: Optional[str] = Header(None, alias="X-Serper-Key"),
):
    try:
        file_path = ""
        if file and file.filename:
            dest = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
            with open(dest, "wb") as buf:
                shutil.copyfileobj(file.file, buf)
            file_path = str(dest)
            logger.info(f"Uploaded: {file.filename} → {dest}")

        user_input = prompt.strip() if prompt and prompt.strip() else "Generate a complete academic report from the uploaded file."

        # Apply user-supplied keys to environment for this request
        if x_openai_key and x_openai_key.strip():
            os.environ["OPENAI_API_KEY"] = x_openai_key.strip()
        elif x_groq_key and x_groq_key.strip():
            os.environ["GROQ_API_KEY"] = x_groq_key.strip()
        if x_serper_key and x_serper_key.strip():
            os.environ["SERPER_API_KEY"] = x_serper_key.strip()

        inputs = {
            "topic": user_input[:100],
            "user_input": user_input,
            "memory_context": "",
            "task_type": "AUTO",
            "code": "",
            "language": "python",
            "youtube_url": "",
            "youtube_output_mode": "summary",
            "lab_manual_path": file_path,
            "planner_goal": "Produce a high-grade academic report using all available expertise.",
            "current_year": str(datetime.now().year),
        }

        logger.info("Starting CrewAI report generation...")
        crew_instance = Cua()
        result = crew_instance.crew(inputs=inputs).kickoff(inputs=inputs)
        result_text = str(result)

        save_chat(user_input, result_text)
        save_note(f"Report: {user_input[:40]}", result_text)

        return {
            "result": result_text,
            "status": "completed",
            "file_name": file.filename if file else "Manual Input",
        }

    except Exception as e:
        logger.error(f"Report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Transcribe ────────────────────────────────────────────────────────────────
@app.post("/api/transcribe")
async def transcribe(
    youtube_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    instructions: Optional[str] = Form(None),
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_groq_key: Optional[str] = Header(None, alias="X-Groq-Key"),
    x_serper_key: Optional[str] = Header(None, alias="X-Serper-Key"),
):
    try:
        if x_openai_key and x_openai_key.strip():
            os.environ["OPENAI_API_KEY"] = x_openai_key.strip()
        elif x_groq_key and x_groq_key.strip():
            os.environ["GROQ_API_KEY"] = x_groq_key.strip()
        if x_serper_key and x_serper_key.strip():
            os.environ["SERPER_API_KEY"] = x_serper_key.strip()
        media_path = None
        if file and file.filename:
            dest = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
            with open(dest, "wb") as buf:
                shutil.copyfileobj(file.file, buf)
            media_path = str(dest)
            logger.info(f"Uploaded media: {file.filename}")

        tool = MultimediaAssistantTool()
        result = tool._run(
            youtube_url=youtube_url or None,
            media_path=media_path,
        )

        save_chat(
            f"Transcribe: {youtube_url or (file.filename if file else 'uploaded file')}",
            result,
        )
        return {"result": result, "status": "completed"}

    except Exception as e:
        logger.error(f"Transcribe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Export ────────────────────────────────────────────────────────────────────
@app.post("/api/report/export")
async def export_report(
    content: str = Form(...),
    format: str = Form("docx"),
    title: str = Form("Academic Report"),
):
    try:
        data = markdown_to_docx(content, title)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": 'attachment; filename="academix_report.docx"'},
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── History ───────────────────────────────────────────────────────────────────
@app.get("/api/history")
async def get_history():
    try:
        history = get_chat_history(limit=100)
        return {"history": [{"user_msg": h[0], "ai_msg": h[1]} for h in history]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history")
async def clear_history():
    try:
        from cua.memory import _get_conn, _LOCK
        with _LOCK:
            conn = _get_conn()
            conn.execute("DELETE FROM chat_history")
            conn.commit()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
