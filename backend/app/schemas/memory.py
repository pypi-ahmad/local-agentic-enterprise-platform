from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoryUpsert(BaseModel):
    scope: str
    key: str
    value: dict = Field(default_factory=dict)


class MemoryView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scope: str
    key: str
    value: dict
    created_at: datetime
