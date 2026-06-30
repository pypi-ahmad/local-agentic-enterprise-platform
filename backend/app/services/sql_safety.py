from dataclasses import dataclass

import sqlglot


@dataclass(slots=True)
class SQLSafetyDecision:
    operation: str
    destructive: bool
    explanation: str


class SQLSafetyService:
    """Parses SQL and determines risk profile before execution."""

    DESTRUCTIVE = {"DELETE", "DROP", "TRUNCATE", "ALTER", "UPDATE", "INSERT"}

    @staticmethod
    def inspect(sql: str, dialect: str = "postgres") -> SQLSafetyDecision:
        statements = sqlglot.parse(sql, read=dialect)
        first = statements[0] if statements else None
        operation = first.key.upper() if first and first.key else "UNKNOWN"
        destructive = operation in SQLSafetyService.DESTRUCTIVE
        explanation = (
            "Query mutates database state and requires explicit confirmation."
            if destructive
            else "Query is read-only and safe for immediate execution."
        )
        return SQLSafetyDecision(operation=operation, destructive=destructive, explanation=explanation)
