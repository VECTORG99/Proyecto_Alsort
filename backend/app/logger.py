import logging
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        module = f"{record.module}:{record.lineno}"
        return f"[{ts}] {record.levelname:<7} {module:<25} {record.getMessage()}"


def setup_logging(level: str = "INFO") -> logging.Logger:
    root = logging.getLogger("alsort")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root.addHandler(handler)

    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)

    return root


logger = logging.getLogger("alsort")
