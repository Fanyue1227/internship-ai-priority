from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.db import get_data_dir
from app.knowledge.generation import answer_with_citations
from app.knowledge.ingest import ingest_raw_documents
from app.knowledge.retrieval import search_knowledge


router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class KnowledgeAskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/ingest")
def ingest() -> dict:
    return ingest_raw_documents(Path(get_data_dir()) / "raw")


@router.post("/search")
def search(body: KnowledgeSearchRequest) -> dict:
    return {"results": search_knowledge(body.query, limit=body.limit)}


@router.post("/ask")
def ask(body: KnowledgeAskRequest) -> dict:
    return answer_with_citations(body.question, limit=body.limit)
