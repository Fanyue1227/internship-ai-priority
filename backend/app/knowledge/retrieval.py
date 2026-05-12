from __future__ import annotations

import re
from collections import Counter

from app.db import get_connection


TOKEN_RE = re.compile(r"[A-Za-z0-9_+#.-]+|[\u4e00-\u9fff]")


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _score(query: str, source_path: str, title: str, section: str, content: str) -> float:
    query_tokens = _tokens(query)
    if not query_tokens:
        return 0.0

    section_lower = section.lower()
    source_lower = source_path.lower()
    title_lower = title.lower()
    content_lower = content.lower()
    content_counts = Counter(_tokens(content))
    score = 0.0

    for token in query_tokens:
        if token in title_lower:
            score += 6.0
        if token in source_lower:
            score += 4.0
        if token in section_lower:
            score += 3.0
        if token in content_lower:
            score += 1.0 + min(content_counts[token], 5) * 0.15

    return score


def search_knowledge(query: str, limit: int = 5) -> list[dict]:
    """Return top chunks using a lightweight keyword scorer.

    This is the first integrated version. The old RAG Lab FAISS layer can be
    swapped in later behind this function without changing Agent tools.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT chunks.id, chunks.source_path, chunks.section, chunks.content, documents.title
            FROM chunks
            JOIN documents ON documents.id = chunks.document_id
            """
        ).fetchall()

    ranked = []
    for row in rows:
        score = _score(query, row["source_path"], row["title"], row["section"], row["content"])
        if score > 0:
            ranked.append(
                {
                    "chunk_id": row["id"],
                    "source_path": row["source_path"],
                    "section": row["section"],
                    "content": row["content"],
                    "score": round(score, 4),
                }
            )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]
