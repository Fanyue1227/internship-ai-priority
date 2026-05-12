from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.board.schemas import BoardDayCreate, BoardTaskCreate, BoardTaskDoneUpdate, BoardTaskUpdate
from app.board.services import (
    create_board_day,
    create_board_task,
    delete_board_task,
    get_board_day,
    list_board_dates,
    update_board_task,
)


router = APIRouter(prefix="/api/board", tags=["board"])


@router.get("/dates")
def read_dates() -> list[str]:
    return list_board_dates()


@router.post("/days")
def create_day(body: BoardDayCreate) -> dict:
    return create_board_day(
        date=str(body.date),
        title=body.title,
        focus=body.focus,
        rationale=body.rationale,
    )


@router.get("/days/{date}")
def read_day(date: str) -> dict:
    day = get_board_day(date)
    if day is None:
        raise HTTPException(status_code=404, detail="Board day not found")
    return day


@router.post("/tasks")
def create_task(body: BoardTaskCreate) -> dict:
    task = create_board_task(
        date=str(body.date),
        title=body.title,
        eta=body.eta,
        how=body.how,
        criteria=body.criteria,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Board day not found")
    return task


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, body: BoardTaskUpdate) -> dict:
    task = update_board_task(
        task_id=task_id,
        title=body.title,
        eta=body.eta,
        how=body.how,
        criteria=body.criteria,
        done=body.done,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Board task not found")
    return task


@router.patch("/tasks/{task_id}/done")
def update_task_done(task_id: int, body: BoardTaskDoneUpdate) -> dict:
    task = update_board_task(task_id=task_id, done=body.done)
    if task is None:
        raise HTTPException(status_code=404, detail="Board task not found")
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict:
    ok = delete_board_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Board task not found")
    return {"ok": True, "task_id": task_id}
