from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.api.board import router as board_router
from app.api.knowledge import router as knowledge_router
from app.api.system import router as system_router
from app.db import init_db


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title="Internship Agent Lab API",
        description="RAG-enhanced task planning agent for AI internship preparation.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root() -> dict:
        return {"ok": True, "name": "Internship Agent Lab"}

    app.include_router(system_router)
    app.include_router(knowledge_router)
    app.include_router(board_router)
    app.include_router(agent_router)
    return app


app = create_app()
