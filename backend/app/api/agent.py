from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.planner import build_evidence_based_plan
from app.agent.tools import execute_tool, list_tools


router = APIRouter(prefix="/api/agent", tags=["agent"])


class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    start_date: str = Field(..., min_length=10, max_length=10)


@router.get("/tools")
def read_tools() -> dict:
    return {"tools": list_tools()}


@router.post("/tools/execute")
def execute(body: ToolExecuteRequest) -> dict:
    try:
        return {"ok": True, "result": execute_tool(body.tool_name, body.arguments)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/plan")
def plan(body: PlanRequest) -> dict:
    return build_evidence_based_plan(body.goal, body.start_date)
