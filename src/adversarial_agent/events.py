"""The event bus: a small, synchronous, one-way observability backbone.

See architecture.md section 5.5. The agent core emits Events; listeners (the
terminal renderer, an optional transcript logger) react to them. The core never
imports the UI -- it only constructs Events and calls ``bus.emit(...)``.

Lifecycle event *values* deliberately match Claude Code's hook names
("PreToolUse", "PostToolUse", "SubagentStart", "SubagentStop", "Stop").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class EventType(str, Enum):
    # --- Content / observability events (this project's own) ---
    USER_INPUT = "user_input"
    THINKING = "thinking"
    AGENT_TEXT = "agent_text"
    ERROR = "error"
    NOTICE = "notice"

    # --- Lifecycle events (named after Claude Code hook points) ---
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    SUBAGENT_START = "SubagentStart"
    SUBAGENT_STOP = "SubagentStop"
    STOP = "Stop"


@dataclass
class Event:
    type: EventType
    depth: int = 0  # 0 = main agent, 1 = sub-agent, ...
    payload: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Listener(Protocol):
    def on_event(self, event: Event) -> None: ...


class EventBus:
    """Synchronous, in-order fan-out to subscribed listeners.

    A faulty listener must never break the agent loop, so ``emit`` swallows
    listener exceptions.
    """

    def __init__(self) -> None:
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def emit(self, event: Event) -> None:
        for listener in self._listeners:
            try:
                listener.on_event(event)
            except Exception:
                # Observability must never crash the agent. Intentionally ignore.
                pass
