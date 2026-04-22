from datetime import date as Date
from typing import Any

from pydantic import BaseModel, Field


class BoardTaskDoneUpdate(BaseModel):
    """Request body for updating a board task checkbox."""

    done: bool


class BoardTaskCreate(BaseModel):
    """Request body for creating one board task."""

    date: Date = Field(..., description="Task date, format YYYY-MM-DD")
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    eta: str = Field(..., min_length=1, description="Estimated time")
    how: list[str] = Field(..., description="Concrete task steps")
    criteria: list[str] = Field(..., description="Acceptance criteria")


class BoardTaskUpdate(BaseModel):
    """Request body for partially updating one board task."""

    title: str | None = Field(None, min_length=1, max_length=100, description="Task title")
    eta: str | None = Field(None, min_length=1, description="Estimated time")
    how: list[str] | None = Field(None, description="Concrete task steps")
    criteria: list[str] | None = Field(None, description="Acceptance criteria")
    done: bool | None = Field(None, description="Whether the task is done")


class BoardAgentProposeRequest(BaseModel):
    """Request body for asking the model to propose a native tool call."""

    date: Date = Field(..., description="Board date, format YYYY-MM-DD")
    message: str = Field(..., min_length=1, description="User natural-language command")


class BoardAgentExecuteRequest(BaseModel):
    """Request body for executing a confirmed tool call."""

    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
