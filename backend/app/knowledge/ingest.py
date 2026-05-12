from __future__ import annotations

from pathlib import Path

from app.db import get_connection
from app.knowledge.chunking import split_markdown_into_chunks


def _extract_title(content: str, path: Path) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def ingest_raw_documents(raw_dir: Path | None = None) -> dict[str, int]:
    """Import markdown files under data/raw into documents/chunks tables."""
    if raw_dir is None:
        from app.db import get_data_dir

        raw_dir = get_data_dir() / "raw"
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    markdown_files = sorted(raw_dir.rglob("*.md"))
    documents = 0
    chunks = 0

    with get_connection() as conn:
        conn.execute("DELETE FROM chunks")
        conn.execute("DELETE FROM documents")

        for path in markdown_files:
            content = path.read_text(encoding="utf-8")
            rel_path = path.relative_to(raw_dir).as_posix()
            title = _extract_title(content, path)
            cursor = conn.execute(
                """
                INSERT INTO documents (source_path, title, content)
                VALUES (?, ?, ?)
                """,
                (rel_path, title, content),
            )
            document_id = cursor.lastrowid
            documents += 1

            for index, chunk in enumerate(split_markdown_into_chunks(content), start=1):
                conn.execute(
                    """
                    INSERT INTO chunks (document_id, source_path, section, content, chunk_index)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        document_id,
                        rel_path,
                        chunk["section"],
                        chunk["content"],
                        index,
                    ),
                )
                chunks += 1

        conn.commit()

    return {"documents": documents, "chunks": chunks}
