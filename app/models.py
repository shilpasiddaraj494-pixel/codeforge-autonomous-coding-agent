from typing import Literal
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    task: str = Field(min_length=3, max_length=5000)


class FileChange(BaseModel):
    path: str
    action: Literal["create", "update", "delete"]
    content: str | None = None
    reason: str = ""


class ChangePlan(BaseModel):
    summary: str
    changes: list[FileChange]
    validation_commands: list[str] = []


class IterationRecord(BaseModel):
    iteration: int
    plan_summary: str
    changed_files: list[str]
    validation_output: str
    success: bool


class AgentResponse(BaseModel):
    task: str
    status: Literal["completed", "failed"]
    summary: str
    iterations: list[IterationRecord]
