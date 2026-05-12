from __future__ import annotations

from app.knowledge.retrieval import search_knowledge


def answer_with_citations(question: str, limit: int = 5) -> dict:
    results = search_knowledge(question, limit=limit)
    if not results:
        return {
            "answer": "知识库中没有检索到足够依据。",
            "citations": [],
        }

    bullet_lines = []
    citations = []
    for result in results:
        snippet = result["content"].replace("\n", " ").strip()
        if len(snippet) > 180:
            snippet = snippet[:180] + "..."
        bullet_lines.append(f"- {snippet}")
        citations.append(
            {
                "source": result["source_path"],
                "section": result["section"],
                "score": result["score"],
            }
        )

    return {
        "answer": "\n".join(bullet_lines),
        "citations": citations,
    }
