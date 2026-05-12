from __future__ import annotations

from app.agent.tools import execute_tool


def build_evidence_based_plan(goal: str, start_date: str) -> dict:
    """Build a deterministic first-pass plan from knowledge search results.

    This keeps the first version usable without requiring a paid model call.
    Later, LLM providers can replace the deterministic task templates.
    """
    evidence = execute_tool(
        "search_knowledge",
        {
            "query": goal,
            "limit": 5,
        },
    )
    return {
        "goal": goal,
        "start_date": start_date,
        "evidence": evidence,
        "recommended_stack": [
            "Python",
            "PyTorch",
            "Hugging Face Transformers",
            "Transformer / LLM basics",
            "LoRA / SFT / PEFT",
            "Agent / Tool Calling",
            "FastAPI / Ollama deployment",
        ],
    }
