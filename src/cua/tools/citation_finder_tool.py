"""
CitationFinderTool — Finds real academic citations.

Priority order:
  1. Elsevier Scopus API  (ELSEVIER_API_KEY) — 90M+ papers, impact factors, citation counts
  2. Semantic Scholar     (free, no key)      — fallback
  3. CrossRef             (free, no key)      — final fallback

Returns properly formatted IEEE and APA citations.
"""

import os
import re
import time
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CitationInput(BaseModel):
    query: str = Field(..., description="Topic or concept to find citations for (e.g., 'semaphore mutual exclusion', 'Python threading GIL')")
    count: int = Field(5, description="Number of citations to return (default 5, max 10)")
    style: str = Field("ieee", description="Citation style: 'ieee' or 'apa'")


# ── Elsevier Scopus ───────────────────────────────────────────────────────────

def _search_scopus(query: str, limit: int) -> list[dict]:
    """Search Elsevier Scopus — highest quality academic database."""
    api_key = os.getenv("ELSEVIER_API_KEY", "").strip()
    if not api_key:
        return []
    try:
        url = "https://api.elsevier.com/content/search/scopus"
        params = {
            "query":   f"TITLE-ABS-KEY({query})",
            "count":   limit,
            "field":   "dc:title,dc:creator,prism:publicationName,prism:coverDate,prism:doi,citedby-count",
            "sort":    "citedby-count",   # most-cited first
            "apiKey":  api_key,
        }
        headers = {"Accept": "application/json"}
        resp = requests.get(url, params=params, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        entries = resp.json().get("search-results", {}).get("entry", [])
        results = []
        for e in entries:
            title = e.get("dc:title", "")
            if not title:
                continue
            # Authors: Scopus returns a single string like "Smith J., Jones A."
            creator = e.get("dc:creator", "")
            authors = [a.strip() for a in creator.split(",")] if creator else []
            date = e.get("prism:coverDate", "")
            year = date[:4] if date else "n.d."
            results.append({
                "title":   title,
                "authors": authors,
                "year":    year,
                "venue":   e.get("prism:publicationName", ""),
                "doi":     e.get("prism:doi", ""),
                "cited":   e.get("citedby-count", ""),
                "source":  "Scopus",
            })
        return results
    except Exception:
        return []


# ── Semantic Scholar ──────────────────────────────────────────────────────────

def _search_semantic_scholar(query: str, limit: int) -> list[dict]:
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query":  query,
            "limit":  limit,
            "fields": "title,authors,year,venue,externalIds",
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        results = []
        for p in resp.json().get("data", []):
            if not p.get("title"):
                continue
            results.append({
                "title":   p.get("title", ""),
                "authors": [a.get("name", "") for a in p.get("authors", [])],
                "year":    p.get("year", "n.d."),
                "venue":   p.get("venue", ""),
                "doi":     p.get("externalIds", {}).get("DOI", ""),
                "source":  "Semantic Scholar",
            })
        return results
    except Exception:
        return []


# ── CrossRef ──────────────────────────────────────────────────────────────────

def _search_crossref(query: str, limit: int) -> list[dict]:
    try:
        url = "https://api.crossref.org/works"
        params = {
            "query":  query,
            "rows":   limit,
            "select": "title,author,published,container-title,DOI",
        }
        headers = {"User-Agent": "Academix/2.0 (mailto:academix@example.com)"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        results = []
        for item in resp.json().get("message", {}).get("items", []):
            titles = item.get("title", [])
            if not titles:
                continue
            authors = []
            for a in item.get("author", []):
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)
            parts = item.get("published", {}).get("date-parts", [[]])
            year = str(parts[0][0]) if parts and parts[0] else "n.d."
            results.append({
                "title":   titles[0],
                "authors": authors,
                "year":    year,
                "venue":   (item.get("container-title") or [""])[0],
                "doi":     item.get("DOI", ""),
                "source":  "CrossRef",
            })
        return results
    except Exception:
        return []


# ── Formatters ────────────────────────────────────────────────────────────────

def _fmt_ieee(ref: dict, idx: int) -> str:
    authors = ref.get("authors", [])
    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) <= 3:
        author_str = ", ".join(authors[:-1]) + " and " + authors[-1]
    else:
        author_str = authors[0] + " et al."

    cited = f" [Cited by {ref['cited']}]" if ref.get("cited") else ""
    src   = f" ({ref.get('source', '')})" if ref.get("source") else ""
    line  = f"[{idx}] {author_str}, \"{ref['title']},\""
    if ref.get("venue"):
        line += f" *{ref['venue']}*,"
    line += f" {ref.get('year', 'n.d.')}."
    if ref.get("doi"):
        line += f" doi: {ref['doi']}"
    line += cited + src
    return line


def _fmt_apa(ref: dict) -> str:
    authors = ref.get("authors", [])
    if not authors:
        author_str = "Unknown Author"
    else:
        formatted = []
        for a in authors[:6]:
            parts = a.split()
            if len(parts) >= 2:
                last = parts[-1]
                initials = ". ".join(p[0] for p in parts[:-1]) + "."
                formatted.append(f"{last}, {initials}")
            else:
                formatted.append(a)
        if len(formatted) > 1:
            author_str = ", ".join(formatted[:-1]) + ", & " + formatted[-1]
        else:
            author_str = formatted[0]
        if len(authors) > 6:
            author_str += ", ... " + formatted[-1]

    line = f"{author_str} ({ref.get('year', 'n.d.')}). {ref['title']}."
    if ref.get("venue"):
        line += f" *{ref['venue']}*."
    if ref.get("doi"):
        line += f" https://doi.org/{ref['doi']}"
    return line


# ── Tool ─────────────────────────────────────────────────────────────────────

class CitationFinderTool(BaseTool):
    name: str = "CitationFinder"
    description: str = (
        "Finds real, verified academic citations using Elsevier Scopus (primary), "
        "Semantic Scholar, and CrossRef. Returns properly formatted IEEE or APA references "
        "sorted by citation count. Use this before writing the References section."
    )
    args_schema: type[BaseModel] = CitationInput

    def _run(self, query: str, count: int = 5, style: str = "ieee") -> str:
        count = min(max(count, 1), 10)
        style = style.lower().strip()

        # Try Scopus first (best quality)
        results = _search_scopus(query, count)
        source_used = "Scopus" if results else None

        # Fill gaps with Semantic Scholar
        if len(results) < count:
            time.sleep(0.3)
            ss = _search_semantic_scholar(query, count - len(results))
            existing = {r["title"].lower() for r in results}
            for r in ss:
                if r["title"].lower() not in existing:
                    results.append(r)
                    existing.add(r["title"].lower())
            if not source_used and results:
                source_used = "Semantic Scholar"

        # Final fallback: CrossRef
        if len(results) < count:
            time.sleep(0.3)
            cr = _search_crossref(query, count - len(results))
            existing = {r["title"].lower() for r in results}
            for r in cr:
                if r["title"].lower() not in existing:
                    results.append(r)
                    existing.add(r["title"].lower())
            if not source_used and results:
                source_used = "CrossRef"

        if not results:
            return (
                "No citations found. Try a more specific academic term "
                "(e.g., 'operating system semaphore Dijkstra')."
            )

        results = results[:count]
        lines = [f"Found {len(results)} citations for: \"{query}\" (via {source_used})\n"]
        for idx, ref in enumerate(results, 1):
            if style == "apa":
                lines.append(f"{idx}. {_fmt_apa(ref)}")
            else:
                lines.append(_fmt_ieee(ref, idx))

        return "\n".join(lines)
