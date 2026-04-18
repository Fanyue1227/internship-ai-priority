from datetime import date as Date

from pydantic import BaseModel, Field


class BoardTaskDoneUpdate(BaseModel):
    """Request body for updating a board task checkbox."""

    done: bool


class BoardTaskCreate(BaseModel):
    """创建看板任务时，前端必须提交的字段。"""

    date: Date = Field(..., description="任务日期，格式 YYYY-MM-DD")
    title: str = Field(..., min_length=1, max_length=100, description="任务标题")
    eta: str = Field(..., min_length=1, description="预计耗时，例如：1 小时")
    how: list[str] = Field(..., description="具体步骤列表")
    criteria: list[str] = Field(..., description="验收标准列表")


class BoardTaskUpdate(BaseModel):
    """更新看板任务时，前端可以提交的字段；都可选，支持部分更新。"""

    title: str | None = Field(None, min_length=1, max_length=100, description="任务标题")
    eta: str | None = Field(None, min_length=1, description="预计耗时，例如：1 小时")
    how: list[str] | None = Field(None, description="具体步骤列表")
    criteria: list[str] | None = Field(None, description="验收标准列表")
    done: bool | None = Field(None, description="是否完成")
