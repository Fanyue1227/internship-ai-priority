from pathlib import Path

from app.agent.tools import execute_tool
from app.board.services import create_board_day, get_board_day
from app.db import configure_database, init_db
from app.knowledge.ingest import ingest_raw_documents


def test_agent_tools_search_knowledge_then_create_task(tmp_path: Path):
    data_dir = tmp_path / "data"
    jobs_dir = data_dir / "raw" / "jobs"
    jobs_dir.mkdir(parents=True)
    (jobs_dir / "llm-role.md").write_text(
        "# 中冶赛迪 - 大模型算法岗\n\n"
        "## 任职要求\n\n"
        "掌握 Python、PyTorch、Hugging Face、LoRA 微调和 Agent 设计。\n",
        encoding="utf-8",
    )

    configure_database(data_dir)
    init_db()
    ingest_raw_documents(data_dir / "raw")
    create_board_day(
        date="2026-04-30",
        title="Day 1",
        focus="模型基础",
        rationale=[],
    )

    search_result = execute_tool("search_knowledge", {"query": "LoRA PyTorch"})
    created = execute_tool(
        "create_task",
        {
            "date": "2026-04-30",
            "title": "完成 LoRA / PEFT 最小实验",
            "eta": "2 小时",
            "how": ["阅读 PEFT 配置", "训练少量 step 并保存 adapter"],
            "criteria": ["能加载 base model + adapter 推理"],
        },
    )
    day = get_board_day("2026-04-30")

    assert "LoRA" in search_result["summary"]
    assert created["title"] == "完成 LoRA / PEFT 最小实验"
    assert day["tasks"][0]["title"] == "完成 LoRA / PEFT 最小实验"
