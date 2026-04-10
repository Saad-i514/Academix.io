import sqlite3
import threading
from pathlib import Path


_DB_PATH = Path("memory.db")
_LOCK = threading.Lock()
_CONN: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _CONN
    if _CONN is None:
        _CONN = sqlite3.connect(_DB_PATH, check_same_thread=False)
        _initialize_db(_CONN)
    return _CONN


def _initialize_db(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            response TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )
    conn.commit()


def save_chat(user_input: str, response: str) -> None:
    with _LOCK:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO chat_history (user_input, response) VALUES (?, ?)",
            (user_input, response),
        )
        conn.commit()


def get_chat_history(limit: int = 5) -> list[tuple[str, str]]:
    try:
        safe_limit = max(1, min(int(limit), 100))  # Cap at 100 for safety
    except (ValueError, TypeError):
        safe_limit = 5
    
    with _LOCK:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT user_input, response FROM chat_history ORDER BY id DESC LIMIT ?",
            (safe_limit,),
        ).fetchall()
    return [(str(user_input), str(response)) for user_input, response in rows]


def save_note(title: str, content: str) -> None:
    with _LOCK:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content),
        )
        conn.commit()


def save_report(content: str, path: str = "report.md") -> None:
    output_path = Path(path)
    output_path.write_text(content, encoding="utf-8")


def search_notes(query: str) -> list[tuple[str, str]]:
    with _LOCK:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT title, content FROM notes WHERE content LIKE ? ORDER BY id DESC",
            (f"%{query}%",),
        ).fetchall()
    return [(str(title), str(content)) for title, content in rows]


def generate_notes_with_memory(user_input: str, limit: int = 5) -> str:
    try:
        safe_limit = max(1, min(int(limit), 100))
    except (ValueError, TypeError):
        safe_limit = 5
    
    past_chats = get_chat_history(limit=safe_limit)
    past_notes = search_notes(user_input)

    memory_context = ""

    for chat_user_input, chat_response in past_chats:
        # Truncate long responses for context
        truncated_response = chat_response[:500] if len(chat_response) > 500 else chat_response
        memory_context += f"User: {chat_user_input}\nAI: {truncated_response}\n"

    for _, note_content in past_notes[:5]:  # Limit to 5 most relevant notes
        memory_context += f"\nRelevant Note: {note_content[:500]}\n"

    if not memory_context.strip():
        return "No relevant past context found."

    prompt = f"""
You are an intelligent university assistant.

Memory:
{memory_context}

User request:
{user_input}

Generate a helpful response using memory if relevant.
""".strip()

    return prompt


def close_memory() -> None:
    global _CONN
    with _LOCK:
        if _CONN is not None:
            _CONN.close()
            _CONN = None