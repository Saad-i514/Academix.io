import os
from typing import Optional


def get_llm(user_openai_key: Optional[str] = None, user_groq_key: Optional[str] = None):
    """
    Returns the most appropriate LLM based on available keys.
    Priority: User OpenAI -> User Groq -> Env OpenAI fallback.
    Returns None if no key found (CrewAI will use OPENAI_API_KEY from env).
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
        return ChatOpenAI(api_key=env_openai, model="gpt-4o-mini")

    # 4. Env Groq key
    env_groq = os.getenv("GROQ_API_KEY", "").strip()
    if env_groq:
        return ChatGroq(api_key=env_groq, model="llama3-70b-8192")

    # No key found — return None, CrewAI will try env vars itself
    return None
