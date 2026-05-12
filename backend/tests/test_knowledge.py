from pathlib import Path

from app.db import configure_database, init_db
from app.knowledge.ingest import ingest_raw_documents
from app.knowledge.retrieval import search_knowledge


def test_ingests_job_markdown_and_searches_by_skill(tmp_path: Path):
    data_dir = tmp_path / "data"
    jobs_dir = data_dir / "raw" / "jobs"
    jobs_dir.mkdir(parents=True)
    (jobs_dir / "future-ai-deploy.md").write_text(
        "# 未来智选 - AI部署实习生\n\n"
        "## 任职要求\n\n"
        "熟悉 LangChain、Ollama、本地大模型部署、FastAPI API 封装。\n",
        encoding="utf-8",
    )

    configure_database(data_dir)
    init_db()
    summary = ingest_raw_documents(data_dir / "raw")

    results = search_knowledge("Ollama FastAPI 部署", limit=3)

    assert summary["documents"] == 1
    assert summary["chunks"] >= 1
    assert results
    assert results[0]["source_path"].endswith("future-ai-deploy.md")
    assert "Ollama" in results[0]["content"]


def test_search_boosts_matching_job_title(tmp_path: Path):
    data_dir = tmp_path / "data"
    jobs_dir = data_dir / "raw" / "jobs"
    jobs_dir.mkdir(parents=True)
    (jobs_dir / "future-ai-deploy.md").write_text(
        "# 未来智选 - AI部署实习生\n\n"
        "## 任职要求\n\n"
        "熟悉 LangChain、Ollama、本地大模型部署、FastAPI API 封装。\n",
        encoding="utf-8",
    )
    (jobs_dir / "other-role.md").write_text(
        "# 其他公司 - 算法实习生\n\n"
        "## 任职要求\n\n"
        "熟悉 AI、部署、算法和技术文档。\n",
        encoding="utf-8",
    )

    configure_database(data_dir)
    init_db()
    ingest_raw_documents(data_dir / "raw")

    results = search_knowledge("未来智选 AI 部署实习生需要准备什么", limit=2)

    assert results[0]["source_path"].endswith("future-ai-deploy.md")
