"""
logger.py — Append-only activity logging for ShellSpark.

Writes one JSON line per event to ~/.shellspark/logs/activity.log
"""

import json
from datetime import datetime, timezone
from .config import ACTIVITY_LOG, ensure_dirs


def log_event(
    query: str,
    command: str,
    risk: str,
    exit_code: int | None = None,
) -> None:
    """
    Append one log entry to activity.log.
    Non-fatal: logging failures are silently ignored.
    """
    ensure_dirs()
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "command": command,
        "risk": risk,
        "exit_code": exit_code,
    }
    try:
        with open(ACTIVITY_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass
