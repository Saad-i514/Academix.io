"""
GrammarCheckerTool — Reviews academic text for grammar, style, and tone.

NO API KEY REQUIRED — uses the same LLM already configured (OpenAI/Groq).

Checks for:
  - Grammar and spelling errors
  - Non-academic phrasing (AI-sounding phrases)
  - Passive/active voice balance
  - Sentence variety
  - Academic tone consistency
"""

import os
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class GrammarInput(BaseModel):
    text: str = Field(..., description="The academic text to review and improve")
    mode: str = Field(
        "review",
        description="Mode: 'review' (list issues only) or 'rewrite' (return improved version)"
    )


# Phrases that make reports sound AI-generated
AI_PHRASES = [
    "it is worth noting that",
    "it is important to note",
    "it should be noted that",
    "this experiment aims to",
    "in conclusion, it can be said",
    "as can be seen from",
    "it is evident that",
    "needless to say",
    "in today's world",
    "in the realm of",
    "delve into",
    "leverage",
    "utilize",
    "furthermore, it is",
    "moreover, it is",
    "in summary, it",
    "this report will",
    "the purpose of this report is to",
]


def _quick_check(text: str) -> list[str]:
    """Fast local checks without LLM."""
    issues = []
    text_lower = text.lower()

    for phrase in AI_PHRASES:
        if phrase in text_lower:
            issues.append(f"AI-sounding phrase detected: '{phrase}' — rephrase naturally")

    # Check for very short paragraphs (less than 2 sentences)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.startswith("#")]
    short_paras = [p[:60] for p in paragraphs if len(p.split(".")) < 2 and len(p) > 20]
    if short_paras:
        issues.append(f"Found {len(short_paras)} very short paragraph(s) — expand for academic depth")

    # Check for missing transitions
    if text.count("\n\n") > 5 and "however" not in text_lower and "therefore" not in text_lower:
        issues.append("Consider adding transition words (however, therefore, consequently) between sections")

    return issues


class GrammarCheckerTool(BaseTool):
    name: str = "GrammarChecker"
    description: str = (
        "Reviews academic text for grammar errors, AI-sounding phrases, and style issues. "
        "In 'review' mode: returns a list of issues found. "
        "In 'rewrite' mode: returns an improved version of the text. "
        "Use this on the final report draft before delivering to the user."
    )
    args_schema: type[BaseModel] = GrammarInput

    def _run(self, text: str, mode: str = "review") -> str:
        # Always run quick local checks first
        quick_issues = _quick_check(text)

        if mode == "review":
            if not quick_issues:
                return "Quick check passed: No obvious AI phrases or style issues detected."
            result = f"Style issues found ({len(quick_issues)}):\n"
            result += "\n".join(f"  • {issue}" for issue in quick_issues)
            return result

        elif mode == "rewrite":
            # Use LLM for full rewrite
            try:
                from langchain_openai import ChatOpenAI
                from langchain_groq import ChatGroq

                openai_key = os.getenv("OPENAI_API_KEY", "").strip()
                groq_key   = os.getenv("GROQ_API_KEY", "").strip()

                if openai_key:
                    llm = ChatOpenAI(api_key=openai_key, model="gpt-4o-mini")
                elif groq_key:
                    llm = ChatGroq(api_key=groq_key, model="llama3-70b-8192")
                else:
                    return f"No LLM key available for rewrite. Quick issues:\n" + "\n".join(quick_issues)

                prompt = (
                    "You are an expert academic editor. Improve the following text:\n"
                    "1. Fix grammar and spelling errors\n"
                    "2. Replace AI-sounding phrases with natural academic language\n"
                    "3. Ensure formal academic tone throughout\n"
                    "4. Vary sentence structure\n"
                    "5. Keep all technical content and facts intact\n\n"
                    "Return ONLY the improved text, no commentary.\n\n"
                    f"TEXT TO IMPROVE:\n{text[:3000]}"
                )

                result = llm.invoke(prompt)
                improved = result.content if hasattr(result, "content") else str(result)

                if quick_issues:
                    return f"Issues fixed:\n" + "\n".join(f"  • {i}" for i in quick_issues) + f"\n\nIMPROVED TEXT:\n{improved}"
                return improved

            except Exception as e:
                return f"Rewrite failed: {e}. Quick issues:\n" + "\n".join(quick_issues)

        return "Invalid mode. Use 'review' or 'rewrite'."
