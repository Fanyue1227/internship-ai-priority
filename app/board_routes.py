from fastapi import APIRouter, HTTPException

from app.agent_tools import execute_tool_action
from app.board_services import (
    create_board_task as create_board_task_service,
    delete_board_task as delete_board_task_service,
    get_board_day,
    list_board_dates,
    update_board_task as update_board_task_service,
    update_board_task_done,
)
from app.schemas import (
    BoardAgentExecuteRequest,
    BoardAgentProposeRequest,
    BoardTaskCreate,
    BoardTaskDoneUpdate,
    BoardTaskUpdate,
)
from app.api_clients import (
    build_board_day_prompt,
    get_agent_tool_proposal,
    get_board_day_ai_plan,
)

router = APIRouter(prefix="/board/api", tags=["board"])


@router.get("/dates")
def read_board_dates():
    """Return all board dates available in app.db."""
    return list_board_dates()


@router.get("/days/{date}")
def read_board_day(date: str):
    """Return one complete board day for the frontend."""
    day = get_board_day(date)
    if day is None:
        raise HTTPException(status_code=404, detail="Board day not found")
    return day


@router.patch("/tasks/{task_id}/done")
def update_task_done(task_id: int, body: BoardTaskDoneUpdate):
    """Persist one board task checkbox state."""
    task = update_board_task_done(task_id=task_id, done=body.done)
    if task is None:
        raise HTTPException(status_code=404, detail="Board task not found")
    return task


@router.post("/tasks")
def create_board_task(body: BoardTaskCreate):
    """Create one board task and save it into board tables."""
    task = create_board_task_service(
        date=str(body.date),
        title=body.title,
        eta=body.eta,
        how=body.how,
        criteria=body.criteria,
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Board day not found")

    return {
        "message": "创建成功",
        "task": task,
    }


@router.patch("/tasks/{task_id}")
def update_board_task(task_id: int, body: BoardTaskUpdate):
    """Update one board task with partial fields."""
    update_data = body.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="至少传一个要更新的字段")

    task = update_board_task_service(
        task_id=task_id,
        title=body.title,
        eta=body.eta,
        how=body.how,
        criteria=body.criteria,
        done=body.done,
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Board task not found")

    return {
        "message": "更新成功",
        "task": task,
    }


@router.delete("/tasks/{task_id}")
def delete_board_task(task_id: int):
    """Delete one board task and its related steps."""
    ok = delete_board_task_service(task_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Board task not found")

    return {
        "message": "删除成功",
        "task_id": task_id,
    }

@router.post("/agent/propose")
def propose_agent_action(body: BoardAgentProposeRequest):
    """Use native model tool calling to propose a board action without executing it."""
    day = get_board_day(str(body.date))
    if day is None:
        raise HTTPException(status_code=404, detail="Board day not found")

    try:
        return get_agent_tool_proposal(
            date=str(body.date),
            message=body.message,
            day=day,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/agent/execute")
def execute_agent_action(body: BoardAgentExecuteRequest):
    """Execute a tool call only after the frontend has confirmed it."""
    try:
        result = execute_tool_action(body.tool_name, body.arguments)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail="Board task or day not found")
    if isinstance(result, dict) and result.get("ok") is False:
        raise HTTPException(status_code=404, detail="Board task or day not found")

    return {
        "ok": True,
        "message": "executed",
        "result": result,
    }


@router.get("/days/{date}/prompt-preview")
def preview_board_day_prompt(date: str):
    try:
        return {
            "date": date,
            "prompt": build_board_day_prompt(date),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/days/{date}/ai-plan")
def create_board_day_ai_plan(
    date: str,
    fallback: bool = True,
    use_model: bool = True,
):
    """Generate an AI task plan from one day's real board data."""
    try:
        result = get_board_day_ai_plan(
            date=date,
            use_fallback=fallback,
            use_model=use_model,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not result["ok"]:
        raise HTTPException(status_code=502, detail=result)

    return result
