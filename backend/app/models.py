from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentRecord:
    source_path: str
    title: str
    content: str


@dataclass(frozen=True)
class ChunkRecord:
    document_id: int
    source_path: str
    section: str
    content: str
    chunk_index: int
