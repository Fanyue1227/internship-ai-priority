from __future__ import annotations

import re


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def split_markdown_into_chunks(content: str) -> list[dict[str, str]]:
    """Split markdown by headings while retaining the section title."""
    chunks: list[dict[str, str]] = []
    current_section = "Document"
    current_lines: list[str] = []

    def flush() -> None:
        text = "\n".join(line for line in current_lines).strip()
        if text:
            chunks.append({"section": current_section, "content": text})

    for line in content.splitlines():
        match = HEADING_RE.match(line)
        if match:
            flush()
            current_section = match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    flush()
    if not chunks and content.strip():
        chunks.append({"section": "Document", "content": content.strip()})
    return chunks
