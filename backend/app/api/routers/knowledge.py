from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import db_session, get_current_user
from app.models import User
from app.schemas.knowledge import KnowledgeResult, KnowledgeSearchRequest
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
service = KnowledgeService()


@router.post("/search", response_model=list[KnowledgeResult])
async def search_knowledge(
    payload: KnowledgeSearchRequest,
    session: AsyncSession = Depends(db_session),
    _: User = Depends(get_current_user),
) -> list[KnowledgeResult]:
    hits = await service.search(session=session, query=payload.query, top_k=payload.top_k)
    return [KnowledgeResult.model_validate(hit) for hit in hits]
