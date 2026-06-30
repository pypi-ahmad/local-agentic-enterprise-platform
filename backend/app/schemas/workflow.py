from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkflowNode(BaseModel):
    id: str
    type: Literal["agent", "condition", "approval", "notification", "terminal"]
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    source: str
    target: str
    condition: str | None = None


class WorkflowDefinitionCreate(BaseModel):
    name: str
    description: str = ""
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]
    is_template: bool = False


class WorkflowDefinitionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    graph: dict[str, Any]
    is_template: bool



class WorkflowRunCreate(BaseModel):
    workflow_definition_id: int
    context: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_definition_id: int
    initiated_by: int
    status: str
    context: dict[str, Any]
    execution_timeline: dict[str, Any]
    created_at: datetime
