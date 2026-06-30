from pydantic import BaseModel, Field


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeResult(BaseModel):
    chunk_id: int
    document_id: int
    score: float
    content: str
    citation: str
