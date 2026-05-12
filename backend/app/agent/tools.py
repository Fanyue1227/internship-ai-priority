from __future__ import annotations

from typing import Any, Callable

from app.board.services import (
    create_board_day,
    create_board_task,
    delete_board_task,
    get_board_day,
    update_board_task,
)
from app.knowledge.generation import answer_with_citations
from app.knowledge.retrieval import search_knowledge


ToolHandler = Callable[[dict[str, Any]], Any]


def _search_knowledge(arguments: dict[str, Any]) -> dict:
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("query is required")

    results = search_knowledge(query, limit=int(arguments.get("limit", 5)))
    summary = "\n".join(
        f"- [{item['source_path']}#{item['section']}] {item['content'][:180].replace(chr(10), ' ')}"
        for item in results
    )
    return {
        "query": query,
        "summary": summary or "知识库中没有检索到相关内容。",
        "sources": [
            {
                "source_path": item["source_path"],
                "section": item["section"],
                "score": item["score"],
            }
            for item in results
        ],
    }


def _ask_knowledge_base(arguments: dict[str, Any]) -> dict:
    question = str(arguments.get("question", "")).strip()
    if not question:
        raise ValueError("question is required")
    return answer_with_citations(question)


def _create_board_day(arguments: dict[str, Any]) -> dict:
    return create_board_day(
        date=str(arguments["date"]),
        title=str(arguments["title"]),
        focus=str(arguments["focus"]),
        rationale=list(arguments.get("rationale", [])),
    )


def _create_task(arguments: dict[str, Any]) -> dict:
    result = create_board_task(
        date=str(arguments["date"]),
        title=str(arguments["title"]),
        eta=str(arguments["eta"]),
        how=list(arguments.get("how", [])),
        criteria=list(arguments.get("criteria", [])),
    )
    if result is None:
        raise ValueError("board day not found")
    return result


def _update_task(arguments: dict[str, Any]) -> dict:
    result = update_board_task(
        task_id=int(arguments["task_id"]),
        title=arguments.get("title"),
        eta=arguments.get("eta"),
        how=arguments.get("how"),
        criteria=arguments.get("criteria"),
        done=arguments.get("done"),
    )
    if result is None:
        raise ValueError("board task not found")
    return result


def _delete_task(arguments: dict[str, Any]) -> dict:
    ok = delete_board_task(int(arguments["task_id"]))
    return {"ok": ok, "task_id": int(arguments["task_id"])}


def _list_day_tasks(arguments: dict[str, Any]) -> dict:
    day = get_board_day(str(arguments["date"]))
    if day is None:
        raise ValueError("board day not found")
    return day


TOOLS: dict[str, ToolHandler] = {
    "search_knowledge": _search_knowledge,
    "ask_knowledge_base": _ask_knowledge_base,
    "create_board_day": _create_board_day,
    "create_task": _create_task,
    "update_task": _update_task,
    "delete_task": _delete_task,
    "list_day_tasks": _list_day_tasks,
}


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    if tool_name not in TOOLS:
        raise ValueError(f"unknown tool: {tool_name}")
    return TOOLS[tool_name](arguments)


def list_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "search_knowledge",
            "description": "Search job descriptions, notes, and technical docs.",
            "required": ["query"],
        },
        {
            "name": "ask_knowledge_base",
            "description": "Answer a question using knowledge base citations.",
            "required": ["question"],
        },
        {
            "name": "create_board_day",
            "description": "Create or update one planning day.",
            "required": ["date", "title", "focus"],
        },
        {
            "name": "create_task",
            "description": "Create one task under an existing day.",
            "required": ["date", "title", "eta"],
        },
        {
            "name": "update_task",
            "description": "Update one board task.",
            "required": ["task_id"],
        },
        {
            "name": "delete_task",
            "description": "Delete one board task.",
            "required": ["task_id"],
        },
        {
            "name": "list_day_tasks",
            "description": "Return one day with all tasks.",
            "required": ["date"],
        },
    ]
