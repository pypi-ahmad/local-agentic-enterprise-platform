from app.services.sql_safety import SQLSafetyService


def test_detects_read_only_query() -> None:
    decision = SQLSafetyService.inspect("SELECT * FROM users")
    assert decision.operation == "SELECT"
    assert decision.destructive is False


def test_detects_destructive_query() -> None:
    decision = SQLSafetyService.inspect("DELETE FROM users WHERE id = 1")
    assert decision.operation == "DELETE"
    assert decision.destructive is True
