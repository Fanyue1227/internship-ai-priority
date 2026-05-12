from __future__ import annotations

from datetime import date as Date

from pydantic import BaseModel, Field


class BoardDayCreate(BaseModel):
    date: Date
    title: str = Field(..., min_length=1)
    focus: str = Field(..., min_length=1)
    rationale: list[str] = Field(default_factory=list)


class BoardTaskCreate(BaseModel):
    date: Date
    title: str = Field(..., min_length=1)
    eta: str = Field(..., min_length=1)
    how: list[str] = Field(default_factory=list)
    criteria: list[str] = Field(default_factory=list)


class BoardTaskUpdate(BaseModel):
    title: str | None = None
    eta: str | None = None
    how: list[str] | None = None
    criteria: list[str] | None = None
    done: bool | None = None


class BoardTaskDoneUpdate(BaseModel):
    done: bool
