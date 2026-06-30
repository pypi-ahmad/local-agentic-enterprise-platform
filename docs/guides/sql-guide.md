# SQL Guide

## Safe SQL Lifecycle

1. Prompt-to-SQL generation with dialect context.
2. Parser-based safety analysis (`sqlglot`).
3. User receives operation explanation.
4. Destructive operations require explicit confirmation.
5. Optional dry-run before execution.

## Supported Query Types

- SELECT
- INSERT
- UPDATE
- DELETE
- JOIN
- GROUP BY
- CTE
- Window functions

## Best Practice

Use generated SQL as draft. Review query plan and row scope before execution.
