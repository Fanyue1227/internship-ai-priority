from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    data_dir: Path = Path(os.getenv("APP_DATA_DIR", PROJECT_ROOT / "data"))
    db_path: Path = Path(os.getenv("APP_DB_PATH", PROJECT_ROOT / "data" / "app.db"))
    model_provider: str = os.getenv("MODEL_PROVIDER", "offline")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    claude_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


def get_settings() -> Settings:
    return Settings()
