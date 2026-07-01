"""Interactive confirmation for destructive actions (architecture.md section 12).

This is intentionally NOT on the event bus: confirmation needs a return value,
whereas the bus is one-way. The Confirmer is called directly from the runner.
"""

from __future__ import annotations

from typing import Any, Callable

from rich.console import Console
from rich.panel import Panel

from .console import console as shared_console


class Confirmer:
    def __init__(
        self,
        console: Console | None = None,
        input_func: Callable[[str], str] | None = None,
    ) -> None:
        self.console = console or shared_console
        self._input = input_func or self.console.input
        self._allow_all = False

    def ask(self, action: str, preview: Any) -> bool:
        if self._allow_all:
            return True

        self.console.print(
            Panel(
                preview if preview is not None else "",
                title=f"confirm: {action}",
                title_align="left",
                border_style="yellow",
            )
        )
        answer = self._input(
            r"[yellow]Proceed? \[y]es / \[n]o / \[a]llow-all this session: [/yellow]"
        ).strip().lower()

        if answer in {"a", "all"}:
            self._allow_all = True
            return True
        return answer in {"y", "yes"}
