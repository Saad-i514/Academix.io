import os
from typing import Optional


def get_llm(user_openai_key: Optional[str] = None, user_groq_key: Optional[str] = None):
    """
    Returns the most appropriate LLM based on available keys.
    Priority: User OpenAI -> User Groq -> Env OpenAI -> Env Groq -> Ollama fallback.
    Returns Ollama as final fallback if no other keys found.
    """
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq

    # 1. User-supplied OpenAI key
    if user_openai_key and user_openai_key.strip():
        try:
            return ChatOpenAI(api_key=user_openai_key.strip(), model="gpt-4o-mini")
        except Exception:
            pass

    # 2. User-supplied Groq key
    if user_groq_key and user_groq_key.strip():
        try:
            return ChatGroq(api_key=user_groq_key.strip(), model="llama3-70b-8192")
        except Exception:
            pass

    # 3. Env OpenAI key (already loaded via dotenv in main.py)
    env_openai = os.getenv("OPENAI_API_KEY", "").strip()
    if env_openai:
        try:
            return ChatOpenAI(api_key=env_openai, model="gpt-4o-mini")
        except Exception:
            pass

    # 4. Env Groq key
    env_groq = os.getenv("GROQ_API_KEY", "").strip()
    if env_groq:
        try:
            return ChatGroq(api_key=env_groq, model="llama3-70b-8192")
        except Exception:
            pass

    # 5. Ollama fallback (always available)
    try:
        return ChatOpenAI(
            base_url="https://ollama.com/api",
            api_key="2368ecc5fe6f48e286db86871dcac887.hFXnM3HygCf0Z0vJFqJWy4lDalso",
            model="llama3.1:8b",  # Default Ollama model
            temperature=0.7,
        )
    except Exception as e:
        print(f"Warning: Ollama fallback failed: {e}")
        # Return None as last resort - CrewAI will try env vars itself
        return None
