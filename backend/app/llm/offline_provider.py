from __future__ import annotations

from app.llm.base import LLMProvider


class OfflineProvider(LLMProvider):
    def generate(self, messages: list[dict[str, str]]) -> str:
        last = messages[-1]["content"] if messages else ""
        return f"[offline] {last}"
