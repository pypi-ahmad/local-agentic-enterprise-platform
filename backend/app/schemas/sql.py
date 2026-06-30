from pydantic import BaseModel, Field


class SQLGenerationRequest(BaseModel):
    prompt: str
    dialect: str = "postgres"
    schema_hint: str = ""


class SQLGenerationResponse(BaseModel):
    sql: str
    explanation: str
    operation: str
    destructive: bool


class SQLExecutionRequest(BaseModel):
    sql: str
    confirm: bool = False
    dry_run: bool = True


class SQLExecutionResponse(BaseModel):
    rows: list[dict] = Field(default_factory=list)
    row_count: int = 0
    execution_ms: int
    safe: bool
