from types import SimpleNamespace

import pytest
from app.api.routers import sql as sql_router
from app.schemas.sql import SQLGenerationRequest
from app.services.sql_service import SQLGenerationError, SQLService
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_generate_retries_once_then_succeeds() -> None:
    service = SQLService()
    prompts: list[str] = []

    async def fake_select(_workload: object) -> SimpleNamespace:
        return SimpleNamespace(selected_model="unit-test-model")

    responses = iter(["", "SELECT id FROM users"])

    async def fake_generate(model: str, prompt: str) -> str:
        _ = model
        prompts.append(prompt)
        return next(responses)

    service.router.select = fake_select  # type: ignore[assignment]
    service.ollama.generate = fake_generate  # type: ignore[assignment]

    sql, decision = await service.generate(
        prompt="show users",
        dialect="postgres",
        schema_hint="users(id)",
    )

    assert sql == "SELECT id FROM users"
    assert decision.operation == "SELECT"
    assert len(prompts) == 2
    assert "Return one valid SQL statement only." in prompts[1]


@pytest.mark.asyncio
async def test_generate_raises_when_model_returns_empty_sql() -> None:
    service = SQLService()

    async def fake_select(_workload: object) -> SimpleNamespace:
        return SimpleNamespace(selected_model="unit-test-model")

    async def fake_generate(model: str, prompt: str) -> str:
        _ = model, prompt
        return "   "

    service.router.select = fake_select  # type: ignore[assignment]
    service.ollama.generate = fake_generate  # type: ignore[assignment]

    with pytest.raises(SQLGenerationError, match="model returned empty SQL output"):
        await service.generate(prompt="show users", dialect="postgres", schema_hint="users(id)")


@pytest.mark.asyncio
async def test_generate_raises_when_sql_not_parseable() -> None:
    service = SQLService()

    async def fake_select(_workload: object) -> SimpleNamespace:
        return SimpleNamespace(selected_model="unit-test-model")

    async def fake_generate(model: str, prompt: str) -> str:
        _ = model, prompt
        return "not sql :::"

    service.router.select = fake_select  # type: ignore[assignment]
    service.ollama.generate = fake_generate  # type: ignore[assignment]

    with pytest.raises(SQLGenerationError, match="generated SQL is not parseable"):
        await service.generate(prompt="show users", dialect="postgres", schema_hint="users(id)")


@pytest.mark.asyncio
async def test_router_maps_generation_error_to_http_422(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_generate(prompt: str, dialect: str, schema_hint: str) -> tuple[str, object]:
        _ = prompt, dialect, schema_hint
        msg = "sql_generation_failed: model returned empty SQL output."
        raise SQLGenerationError(msg)

    monkeypatch.setattr(sql_router.service, "generate", fake_generate)

    with pytest.raises(HTTPException) as error:
        await sql_router.generate_sql(SQLGenerationRequest(prompt="show users"), object())

    assert error.value.status_code == 422
    assert error.value.detail["code"] == "sql_generation_failed"

