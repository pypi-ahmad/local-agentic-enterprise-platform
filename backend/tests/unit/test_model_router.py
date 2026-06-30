import pytest
from app.services.model_router import ModelRouter, Workload


@pytest.mark.asyncio
async def test_model_router_selects_default_when_none_available() -> None:
    router = ModelRouter()
    
    async def _empty() -> list[str]:
        return []

    router._safe_model_list = _empty  # type: ignore[assignment]
    selection = await router.select(Workload.CHAT)
    assert selection.selected_model
    assert selection.fallback_model
