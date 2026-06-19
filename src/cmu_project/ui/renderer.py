"""ConsoleRenderer: a bus listener that renders events to the terminal.

See architecture.md section 11. This is the only module that imports rich
rendering primitives for agent output. It translates each Event into a panel or
line, using ``event.depth`` to indent and recolor nested sub-agent activity.
"""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from ..events import Event, EventType


class ConsoleRenderer:
    """Implements the Listener protocol (duck-typed via ``on_event``)."""

    def __init__(self, console: Console) -> None:
        self.console = console
        self._handlers = {
            EventType.USER_INPUT: self._user_input,
            EventType.THINKING: self._thinking,
            EventType.AGENT_TEXT: self._agent_text,
            EventType.PRE_TOOL_USE: self._pre_tool_use,
            EventType.POST_TOOL_USE: self._post_tool_use,
            EventType.SUBAGENT_START: self._subagent_start,
            EventType.SUBAGENT_STOP: self._subagent_stop,
            EventType.STOP: self._stop,
            EventType.ERROR: self._error,
            EventType.NOTICE: self._notice,
        }

    def on_event(self, event: Event) -> None:
        handler = self._handlers.get(event.type)
        if handler is not None:
            handler(event)

    # -- helpers ---------------------------------------------------------

    def _accent(self, depth: int) -> str:
        return "cyan" if depth == 0 else "magenta"

    def _emit(self, renderable: Any, depth: int) -> None:
        if depth > 0:
            renderable = Padding(renderable, (0, 0, 0, 2 * depth))
        self.console.print(renderable)

    # -- per-event renderers --------------------------------------------

    def _user_input(self, event: Event) -> None:
        text = event.payload.get("text", "")
        self._emit(Text.assemble(("you ", "bold green"), (text, "default")), event.depth)

    def _thinking(self, event: Event) -> None:
        text = (event.payload.get("text") or "").strip()
        if not text:
            return
        panel = Panel(
            Text(text, style="italic dim"),
            title="thinking",
            title_align="left",
            border_style="grey42",
        )
        self._emit(panel, event.depth)

    def _agent_text(self, event: Event) -> None:
        text = (event.payload.get("text") or "").strip()
        if not text:
            return
        self._emit(Markdown(text), event.depth)

    def _pre_tool_use(self, event: Event) -> None:
        name = event.payload.get("name", "?")
        tool_input = event.payload.get("input", {})
        body = Text(_pretty(tool_input), style="default")
        panel = Panel(
            body,
            title=f"-> {name}",
            title_align="left",
            border_style=self._accent(event.depth),
        )
        self._emit(panel, event.depth)

    def _post_tool_use(self, event: Event) -> None:
        name = event.payload.get("name", "?")
        content = str(event.payload.get("content", ""))
        is_error = bool(event.payload.get("is_error"))
        border = "red" if is_error else "green"
        panel = Panel(
            Text(content),
            title=f"<- {name}{' (error)' if is_error else ''}",
            title_align="left",
            border_style=border,
        )
        self._emit(panel, event.depth)

    def _subagent_start(self, event: Event) -> None:
        task = event.payload.get("task", "")
        panel = Panel(
            Text(task, style="default"),
            title="sub-agent: start",
            title_align="left",
            border_style="magenta",
        )
        self._emit(panel, event.depth)

    def _subagent_stop(self, event: Event) -> None:
        summary = event.payload.get("summary", "")
        panel = Panel(
            Group(Markdown(summary)) if summary else Text("(no summary)"),
            title="sub-agent: done",
            title_align="left",
            border_style="magenta",
        )
        self._emit(panel, event.depth)

    def _stop(self, event: Event) -> None:
        self.console.rule(style="grey30")

    def _error(self, event: Event) -> None:
        message = event.payload.get("message", "")
        self._emit(Text.assemble(("error: ", "bold red"), (message, "red")), event.depth)

    def _notice(self, event: Event) -> None:
        message = event.payload.get("message", "")
        self._emit(Text(message, style="yellow"), event.depth)


def _pretty(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)
