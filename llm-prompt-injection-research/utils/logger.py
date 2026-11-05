"""Latency and interaction CSV logger for baseline / protected evaluation."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

LOG_COLUMNS = [
    "timestamp",
    "session_id",
    "user_input",
    "model_response",
    "latency_ms",
    "app_version",
    "blocked",
    "block_reason",
    "defense_stages",
]

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "baseline_interactions.csv"
PROTECTED_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "protected_interactions.csv"


def _ensure_log_file(log_path: Path) -> None:
    """Create the log file with a CSV header if it does not already exist."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists() or log_path.stat().st_size == 0:
        with log_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=LOG_COLUMNS)
            writer.writeheader()


def log_interaction(
    session_id: str,
    user_input: str,
    model_response: str,
    latency_ms: float,
    app_version: str = "baseline",
    log_path: Path | None = None,
    blocked: bool = False,
    block_reason: str | None = None,
    defense_stages: str | None = None,
) -> None:
    """
    Append a single chat interaction (and optional defense metadata) to CSV.
    """
    if log_path is not None:
        destination = Path(log_path)
    elif app_version == "protected":
        destination = PROTECTED_LOG_PATH
    else:
        destination = DEFAULT_LOG_PATH

    _ensure_log_file(destination)

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user_input": user_input,
        "model_response": model_response,
        "latency_ms": f"{latency_ms:.2f}",
        "app_version": app_version,
        "blocked": "true" if blocked else "false",
        "block_reason": block_reason or "",
        "defense_stages": defense_stages or "",
    }

    with destination.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_COLUMNS)
        writer.writerow(row)
