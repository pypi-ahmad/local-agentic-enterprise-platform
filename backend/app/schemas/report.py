from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportCreateRequest(BaseModel):
    name: str
    report_type: str
    payload: dict = Field(default_factory=dict)


class ReportView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    report_type: str
    payload: dict
    file_path: str
    created_at: datetime
