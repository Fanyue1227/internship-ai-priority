from __future__ import annotations

from app.config import get_settings
from app.llm.base import LLMProvider
from app.llm.offline_provider import OfflineProvider
from app.llm.ollama_provider import OllamaProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.model_provider.lower() == "ollama":
        return OllamaProvider()
    return OfflineProvider()
