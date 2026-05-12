from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.db import get_db_path


router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status")
def status() -> dict:
    settings = get_settings()
    return {
        "ok": True,
        "model_provider": settings.model_provider,
        "db_path": str(get_db_path()),
    }
