# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "app.db"
SEED_PATH = ROOT / "data" / "board_seed.json"

DAY = "2026-04-22"
BACKUP_DAY = "2026-04-27"

TEACHING_DAY = {
    "title": "2026-04-22 RAG Lab 学习日",
    "focus": "今天按从数据到问答的顺序完整学习 Open Source RAG Lab，重点是看懂每个模块负责什么、数据如何流动，以及为什么这个项目选择技术文档作为核心语料。",
    "rationale": [
        "项目已经能运行，但如果你讲不清输入、处理中间层和输出，这个项目对你就还是黑盒。",
        "今天不再继续堆功能，而是把已有实现拆开理解，确保你能独立解释每个模块的职责和上下游关系。",
        "学完这一天后，你应该能从 README 一路讲到检索和回答生成，也能用自己的话复述整个项目。"
    ],
    "tasks": [
        {
            "id": "raglab-learning-overview",
            "title": "先建立项目全景图",
            "eta": "50 分钟",
            "how": [
                "先看 open-source-rag-lab/README.md，明确这个项目解决什么问题、输入是什么、输出是什么。",
                "再看 app、scripts、data、prompts、tests 这些目录，先建立模块地图，不要一上来钻进细节。",
                "用自己的话回答一句：这个项目为什么不是金融问答，而是技术文档问答。"
            ],
            "criteria": [
                "你能在 3 分钟内说明这个项目的定位、主要功能和完整链路。"
            ],
            "done": False,
        },
        {
            "id": "raglab-learning-ingest",
            "title": "理解语料入口与切块逻辑",
            "eta": "1.5 小时",
            "how": [
                "先看 data/raw 和 SOURCE_INVENTORY.md，知道当前收录了哪些官方项目文档，以及这些文档为什么适合做 RAG 语料。",
                "阅读 app/ingest.py，弄清 Markdown 和 Notebook 是怎么被转换成 DocumentRecord 的。",
                "阅读 app/chunking.py，弄清一个文档如何被拆成多个 chunk，section_title 和 chunk_index 为什么重要。"
            ],
            "criteria": [
                "你能清楚说出 DocumentRecord 和 ChunkRecord 的区别，并解释切块为什么直接影响后续检索效果。"
            ],
            "done": False,
        },
        {
            "id": "raglab-learning-db",
            "title": "理解 SQLite 建库和数据落盘",
            "eta": "1 小时",
            "how": [
                "阅读 app/db.py，确认 documents、chunks、qa_runs、eval_runs 四张表分别存什么。",
                "阅读 scripts/build_corpus.py，梳理原始文档是怎样经过导入和切块后写进 SQLite 的。",
                "重点理解 documents 和 chunks 为什么要分层保存，而不是把整篇文档直接拿去检索。"
            ],
            "criteria": [
                "你能画出 raw 文档到 SQLite 的流转过程，并说明每张核心表的职责。"
            ],
            "done": False,
        },
        {
            "id": "raglab-learning-index",
            "title": "理解 embedding 和 FAISS 索引",
            "eta": "1 小时",
            "how": [
                "阅读 app/embeddings.py，理解文本是如何变成向量的，以及没有 OpenAI key 时为什么还能走离线 fallback。",
                "阅读 scripts/build_index.py，理解 chunks 是怎样分批转向量并写入 FAISS 索引文件的。",
                "搞清楚 data/vector 目录里 chunks.faiss 和 chunk_ids.json 各自负责什么。"
            ],
            "criteria": [
                "你能解释向量索引的作用，并说明 FAISS 文件和数据库之间是如何对应的。"
            ],
            "done": False,
        },
        {
            "id": "raglab-learning-retrieval-generation",
            "title": "理解检索与回答生成主链",
            "eta": "1.5 小时",
            "how": [
                "阅读 app/retrieval.py，区分关键词检索、向量检索和混合检索分别在做什么。",
                "阅读 app/generation.py，理解问题、检索结果、Prompt 模板是怎样组装成最终回答的。",
                "拿一个问题例如“LangChain 是什么？”顺着代码手动走一遍，直到看懂引用是怎么带出来的。"
            ],
            "criteria": [
                "你能完整复述一条用户问题从输入到回答输出的执行链路。"
            ],
            "done": False,
        },
        {
            "id": "raglab-learning-ui-eval",
            "title": "理解页面、评测和分析层",
            "eta": "1 小时",
            "how": [
                "阅读 app/main.py，先搞清页面层负责接收什么输入、展示什么结果。",
                "阅读 app/evaluation.py 和 scripts/run_eval.py，理解 benchmark 问题和 Prompt 对比是在怎么跑。",
                "阅读 app/analytics.py，弄清它展示的统计信息从哪里来，为什么这些指标能帮助判断知识库质量。"
            ],
            "criteria": [
                "你能说明 UI、评测、分析三层分别服务什么目标，而不是把它们都当成展示页面。"
            ],
            "done": False,
        },
        {
            "id": "raglab-learning-retell",
            "title": "做一次完整复述与面试表达",
            "eta": "1 小时",
            "how": [
                "按照“项目目标 -> 数据来源 -> 建库 -> 索引 -> 检索 -> 生成 -> 评测”的顺序写一版 300 到 500 字项目讲解。",
                "再压缩成 90 秒口头版本，要求不看代码也能讲清楚主链。",
                "最后回答 3 个追问：为什么用技术文档、为什么要 SQLite 分层、为什么要做 Prompt 对比。"
            ],
            "criteria": [
                "你能独立讲清这个项目，并且回答追问时不依赖我替你补逻辑。"
            ],
            "done": False,
        },
    ],
}


def replace_day_in_seed() -> None:
    with SEED_PATH.open("r", encoding="utf-8") as fh:
        seed = json.load(fh)
    seed["days"][DAY] = TEACHING_DAY
    if BACKUP_DAY in seed["days"]:
        seed["days"][BACKUP_DAY]["title"] = "2026-04-27 知识库底座日"
    with SEED_PATH.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(seed, fh, ensure_ascii=False, indent=4)
        fh.write("\n")


def replace_day_in_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        task_ids = [
            row[0]
            for row in conn.execute(
                "SELECT id FROM board_tasks WHERE day_date = ? ORDER BY sort_order, id",
                (DAY,),
            ).fetchall()
        ]
        for task_id in task_ids:
            conn.execute("DELETE FROM board_task_steps WHERE task_id = ?", (task_id,))
        conn.execute("DELETE FROM board_tasks WHERE day_date = ?", (DAY,))
        conn.execute("DELETE FROM board_day_rationale WHERE day_date = ?", (DAY,))
        conn.execute("DELETE FROM board_days WHERE date = ?", (DAY,))

        conn.execute(
            "INSERT INTO board_days (date, title, focus) VALUES (?, ?, ?)",
            (DAY, TEACHING_DAY["title"], TEACHING_DAY["focus"]),
        )
        for index, line in enumerate(TEACHING_DAY["rationale"]):
            conn.execute(
                """
                INSERT INTO board_day_rationale (day_date, content, sort_order)
                VALUES (?, ?, ?)
                """,
                (DAY, line, index),
            )

        for sort_order, task in enumerate(TEACHING_DAY["tasks"]):
            cursor = conn.execute(
                """
                INSERT INTO board_tasks (day_date, task_key, title, eta, done, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (DAY, task["id"], task["title"], task["eta"], int(task["done"]), sort_order),
            )
            task_id = cursor.lastrowid
            for step_index, step in enumerate(task["how"]):
                conn.execute(
                    """
                    INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, "how", step, step_index),
                )
            for step_index, step in enumerate(task["criteria"]):
                conn.execute(
                    """
                    INSERT INTO board_task_steps (task_id, step_type, content, sort_order)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, "criteria", step, step_index),
                )

        conn.execute(
            "UPDATE board_days SET title = ? WHERE date = ?",
            ("2026-04-27 知识库底座日", BACKUP_DAY),
        )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    replace_day_in_seed()
    replace_day_in_db()
    print(f"Repaired board data for {DAY}.")


if __name__ == "__main__":
    main()
