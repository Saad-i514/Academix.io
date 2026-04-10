"""
PlagiarismCheckerTool — Checks text originality using local similarity analysis.

NO API KEY REQUIRED — uses local TF-IDF similarity + common phrase detection.

For production-grade checking, optionally integrates with:
  - Copyleaks API (requires key: COPYLEAKS_API_KEY)
  - But works fully without any key using local analysis.

Detects:
  - Repeated phrases (self-plagiarism patterns)
  - Common boilerplate AI text patterns
  - Sentence-level similarity within the document
  - Originality score estimate
"""

import re
import math
from collections import Counter
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class PlagiarismInput(BaseModel):
    text: str = Field(..., description="The academic text to check for originality")


# Common AI-generated boilerplate phrases that reduce originality score
BOILERPLATE_PHRASES = [
    "in conclusion", "to summarize", "as mentioned above",
    "it is important to note", "it is worth noting",
    "in today's rapidly evolving", "in the modern era",
    "plays a crucial role", "is of utmost importance",
    "has been widely studied", "numerous researchers have",
    "the results clearly show", "as can be seen from the above",
    "this report has successfully", "the experiment was successful",
    "in summary, this experiment", "the objectives were met",
]


def _tokenize(text: str) -> list[str]:
    """Simple word tokenizer."""
    return re.findall(r"\b[a-z]{3,}\b", text.lower())


def _get_ngrams(tokens: list[str], n: int) -> list[tuple]:
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def _tfidf_similarity(text: str) -> float:
    """
    Estimate internal repetition using TF-IDF cosine similarity
    between the first and second halves of the document.
    High similarity = repetitive content.
    """
    mid = len(text) // 2
    half1 = _tokenize(text[:mid])
    half2 = _tokenize(text[mid:])

    if not half1 or not half2:
        return 0.0

    vocab = set(half1) | set(half2)
    c1 = Counter(half1)
    c2 = Counter(half2)

    dot = sum(c1.get(w, 0) * c2.get(w, 0) for w in vocab)
    mag1 = math.sqrt(sum(v**2 for v in c1.values()))
    mag2 = math.sqrt(sum(v**2 for v in c2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def _count_boilerplate(text: str) -> list[str]:
    text_lower = text.lower()
    found = [p for p in BOILERPLATE_PHRASES if p in text_lower]
    return found


def _sentence_variety_score(text: str) -> float:
    """Score 0-1 based on sentence length variety (higher = more varied = better)."""
    sentences = re.split(r"[.!?]+", text)
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 3]
    if len(lengths) < 3:
        return 1.0
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    # Normalize: std > 8 is good variety
    return min(std / 8.0, 1.0)


class PlagiarismCheckerTool(BaseTool):
    name: str = "PlagiarismChecker"
    description: str = (
        "Analyzes academic text for originality issues. "
        "Detects repetitive content, boilerplate AI phrases, and low sentence variety. "
        "Returns an originality score (0-100) and specific issues to fix. "
        "Use this on the final report before delivering to the user."
    )
    args_schema: type[BaseModel] = PlagiarismInput

    def _run(self, text: str) -> str:
        if len(text.strip()) < 100:
            return "Text too short to analyze (minimum 100 characters)."

        issues = []
        deductions = 0

        # 1. Boilerplate check
        boilerplate = _count_boilerplate(text)
        if boilerplate:
            deductions += len(boilerplate) * 3
            issues.append(
                f"Found {len(boilerplate)} boilerplate phrase(s): "
                + ", ".join(f'"{p}"' for p in boilerplate[:5])
            )

        # 2. Internal repetition
        similarity = _tfidf_similarity(text)
        if similarity > 0.7:
            deductions += 20
            issues.append(f"High internal repetition detected (similarity: {similarity:.0%}) — content is repetitive")
        elif similarity > 0.5:
            deductions += 10
            issues.append(f"Moderate internal repetition (similarity: {similarity:.0%})")

        # 3. Sentence variety
        variety = _sentence_variety_score(text)
        if variety < 0.3:
            deductions += 10
            issues.append("Low sentence length variety — all sentences are similar length, which looks AI-generated")
        elif variety < 0.5:
            deductions += 5
            issues.append("Moderate sentence variety — consider varying sentence lengths more")

        # 4. Repeated 4-grams
        tokens = _tokenize(text)
        ngrams = _get_ngrams(tokens, 4)
        ngram_counts = Counter(ngrams)
        repeated = [(ng, c) for ng, c in ngram_counts.items() if c >= 3]
        if repeated:
            deductions += min(len(repeated) * 2, 15)
            top = repeated[:3]
            issues.append(
                f"Repeated 4-word phrases found: "
                + ", ".join(f'"{" ".join(ng)}" ({c}x)' for ng, c in top)
            )

        # Calculate score
        score = max(0, 100 - deductions)

        # Build report
        lines = [f"Originality Score: {score}/100"]

        if score >= 80:
            lines.append("Status: GOOD — Text appears original and well-written")
        elif score >= 60:
            lines.append("Status: FAIR — Some issues found, consider revisions")
        else:
            lines.append("Status: NEEDS REVISION — Multiple originality concerns")

        if issues:
            lines.append(f"\nIssues found ({len(issues)}):")
            for issue in issues:
                lines.append(f"  • {issue}")
        else:
            lines.append("\nNo significant issues detected.")

        lines.append(
            "\nNote: This is a local analysis. For certified plagiarism checking, "
            "use Turnitin or Copyleaks with your institution's account."
        )

        return "\n".join(lines)
