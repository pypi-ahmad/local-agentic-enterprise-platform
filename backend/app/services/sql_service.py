from time import perf_counter

import sqlglot
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlglot.errors import ParseError

from app.services.model_router import ModelRouter, Workload
from app.services.ollama_client import OllamaClient
from app.services.sql_safety import SQLSafetyDecision, SQLSafetyService


class SQLGenerationError(ValueError):
    """Raised when generated SQL is missing or invalid."""


class SQLService:
    """Natural-language to SQL generation plus guarded execution."""

    def __init__(self) -> None:
        self.router = ModelRouter()
        self.ollama = OllamaClient()
        self.safety = SQLSafetyService()

    async def generate(self, prompt: str, dialect: str, schema_hint: str = "") -> tuple[str, SQLSafetyDecision]:
        model = (await self.router.select(Workload.SQL)).selected_model
        prompts = [
            self._build_prompt(prompt=prompt, dialect=dialect, schema_hint=schema_hint, strict=False),
            self._build_prompt(prompt=prompt, dialect=dialect, schema_hint=schema_hint, strict=True),
        ]

        for index, full_prompt in enumerate(prompts):
            raw_sql = await self.ollama.generate(model=model, prompt=full_prompt)
            sql = self._normalize_sql(raw_sql)
            if not sql:
                if index == 0:
                    continue
                msg = "sql_generation_failed: model returned empty SQL output."
                raise SQLGenerationError(msg)

            decision = self._validate_generated_sql(sql=sql, dialect=dialect)
            return sql, decision

        msg = "sql_generation_failed: model returned empty SQL output."
        raise SQLGenerationError(msg)

    @staticmethod
    def _build_prompt(prompt: str, dialect: str, schema_hint: str, strict: bool) -> str:
        suffix = "Return one valid SQL statement only. No markdown, comments, or explanation." if strict else ""
        return (
            "Convert user request to SQL. Return SQL only.\n"
            f"Dialect: {dialect}\n"
            f"Schema hint: {schema_hint}\n"
            f"Request: {prompt}\n"
            "Ensure safe and explicit column usage.\n"
            f"{suffix}"
        ).strip()

    @staticmethod
    def _normalize_sql(sql: str) -> str:
        return sql.strip().strip("`").strip()

    def _validate_generated_sql(self, sql: str, dialect: str) -> SQLSafetyDecision:
        try:
            statements = sqlglot.parse(sql, read=dialect)
        except ParseError as exc:
            msg = "sql_generation_failed: generated SQL is not parseable."
            raise SQLGenerationError(msg) from exc

        first = statements[0] if statements else None
        first_key = (first.key or "").upper() if first and hasattr(first, "key") else ""
        if not first_key or first_key == "UNKNOWN":
            msg = "sql_generation_failed: generated SQL operation is unknown."
            raise SQLGenerationError(msg)

        decision = self.safety.inspect(sql, dialect=dialect)
        if decision.operation == "UNKNOWN":
            msg = "sql_generation_failed: generated SQL operation is unknown."
            raise SQLGenerationError(msg)
        return decision

    async def execute(
        self,
        session: AsyncSession,
        engine: AsyncEngine,
        sql: str,
        confirm: bool,
        dry_run: bool,
    ) -> tuple[list[dict], int, int, SQLSafetyDecision]:
        decision = self.safety.inspect(sql)
        if decision.destructive and not confirm:
            msg = "Destructive SQL requires explicit confirmation."
            raise PermissionError(msg)

        start = perf_counter()
        rows: list[dict] = []
        row_count = 0
        if dry_run:
            execution_ms = int((perf_counter() - start) * 1000)
            return rows, row_count, execution_ms, decision

        async with engine.begin() as connection:
            result = await connection.execute(text(sql))
            if result.returns_rows:
                maps = result.mappings().all()
                rows = [dict(row) for row in maps]
                row_count = len(rows)
            else:
                row_count = result.rowcount or 0
        execution_ms = int((perf_counter() - start) * 1000)
        await session.commit()
        return rows, row_count, execution_ms, decision
