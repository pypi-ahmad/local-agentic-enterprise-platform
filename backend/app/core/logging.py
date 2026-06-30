import sys
from typing import Any

from loguru import logger

from app.core.config import get_settings


class InterceptHandler:
    """Route stdlib logs through loguru."""

    def write(self, message: str) -> None:
        if message.strip():
            logger.info(message.strip())

    def flush(self) -> None:
        return None


def setup_logging() -> None:
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=False,
        serialize=True,
        level="INFO",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        settings.logs_dir / "app.log",
        rotation="100 MB",
        retention="7 days",
        serialize=True,
        level="INFO",
    )


def bind_context(**kwargs: Any) -> Any:
    return logger.bind(**kwargs)
