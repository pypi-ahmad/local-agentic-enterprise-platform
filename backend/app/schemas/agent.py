from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentTaskRequest(BaseModel):
    agent_name: str
    task: str
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    require_approval: bool = False


class AgentTaskResult(BaseModel):
    status: str
    agent_name: str
    model_used: str
    output: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


class AgentExecutionTrace(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_name: str
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    duration_ms: int
    error: str
    created_at: datetime
