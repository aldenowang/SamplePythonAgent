"""TranscriptListener: append every event to a JSONL file.

Demonstrates the payoff of the event-driven design (architecture.md section 11):
a second sink can be added without touching the agent core. Enabled via the
AGENT_TRANSCRIPT env var / config flag.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..events import Event


class TranscriptListener:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def on_event(self, event: Event) -> None:
        record: dict[str, Any] = {
            "type": event.type.value,
            "depth": event.depth,
            "payload": _safe(event.payload),
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _safe(payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in payload.items():
        try:
            json.dumps(value)
            out[key] = value
        except (TypeError, ValueError):
            out[key] = str(value)
    return out
