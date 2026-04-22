from typing import Any, Callable

from app.board_services import (
    create_board_task as create_board_task_service,
    delete_board_task as delete_board_task_service,
    update_board_task as update_board_task_service,
    update_board_task_done,
)


AGENT_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "update_task_done",
            "description": "Mark one board task as done or not done.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The numeric id of the board task.",
                    },
                    "done": {
                        "type": "boolean",
                        "description": "true means done; false means not done.",
                    },
                },
                "required": ["task_id", "done"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_board_task",
            "description": "Create one task in a board day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "title": {"type": "string"},
                    "eta": {"type": "string"},
                    "how": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Concrete steps for the task.",
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Acceptance criteria for the task.",
                    },
                },
                "required": ["date", "title", "eta", "how", "criteria"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_board_task",
            "description": "Update one existing board task. Only pass fields that should change.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "eta": {"type": "string"},
                    "how": {"type": "array", "items": {"type": "string"}},
                    "criteria": {"type": "array", "items": {"type": "string"}},
                    "done": {"type": "boolean"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_board_task",
            "description": "Delete one existing board task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
]


def get_agent_tool_definitions() -> list[dict[str, Any]]:
    """Return provider-native tool schemas for the task board agent."""
    return AGENT_TOOL_DEFINITIONS


def _update_task_done(arguments: dict[str, Any]) -> dict[str, Any] | None:
    return update_board_task_done(
        task_id=int(arguments["task_id"]),
        done=bool(arguments["done"]),
    )


def _create_board_task(arguments: dict[str, Any]) -> dict[str, Any] | None:
    return create_board_task_service(
        date=str(arguments["date"]),
        title=str(arguments["title"]),
        eta=str(arguments["eta"]),
        how=list(arguments["how"]),
        criteria=list(arguments["criteria"]),
    )


def _update_board_task(arguments: dict[str, Any]) -> dict[str, Any] | None:
    return update_board_task_service(
        task_id=int(arguments["task_id"]),
        title=arguments.get("title"),
        eta=arguments.get("eta"),
        how=arguments.get("how"),
        criteria=arguments.get("criteria"),
        done=arguments.get("done"),
    )


def _delete_board_task(arguments: dict[str, Any]) -> dict[str, Any]:
    task_id = int(arguments["task_id"])
    deleted = delete_board_task_service(task_id)
    if not deleted:
        return {"ok": False, "task_id": task_id}
    return {"ok": True, "task_id": task_id}


TOOL_EXECUTORS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "update_task_done": _update_task_done,
    "create_board_task": _create_board_task,
    "update_board_task": _update_board_task,
    "delete_board_task": _delete_board_task,
}


def describe_tool_action(tool_name: str, arguments: dict[str, Any]) -> str:
    """Build a short confirmation text for the frontend."""
    if tool_name == "update_task_done":
        state = "标记为完成" if arguments.get("done") else "标记为未完成"
        return f"确认要把任务 #{arguments.get('task_id')} {state}吗？"
    if tool_name == "create_board_task":
        return f"确认要创建任务“{arguments.get('title')}”吗？"
    if tool_name == "update_board_task":
        return f"确认要更新任务 #{arguments.get('task_id')} 吗？"
    if tool_name == "delete_board_task":
        return f"确认要删除任务 #{arguments.get('task_id')} 吗？"
    return f"确认要执行工具“{tool_name}”吗？"


def execute_tool_action(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Execute one allowed tool call after the frontend has confirmed it."""
    executor = TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        raise ValueError(f"Unknown or disallowed tool: {tool_name}")
    return executor(arguments)
