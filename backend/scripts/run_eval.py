from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.knowledge.retrieval import search_knowledge


QUESTIONS = [
    "这几个岗位共同需要哪些技术栈？",
    "未来智选 AI 部署实习生需要准备什么？",
    "中冶赛迪大模型算法岗需要哪些大模型能力？",
]


def main() -> None:
    for question in QUESTIONS:
        print(f"\n## {question}")
        for item in search_knowledge(question, limit=3):
            print(f"- {item['source_path']}#{item['section']} score={item['score']}")


if __name__ == "__main__":
    main()
