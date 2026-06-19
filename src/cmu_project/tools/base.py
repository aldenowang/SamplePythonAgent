"""Tool framework: the Tool interface, result type, and execution context.

See architecture.md section 9. Tools never touch the UI directly; they emit
events via ``ctx.bus`` and (for destructive actions) ask ``ctx.confirm``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from ..config import AgentConfig
from ..conversation import tool_result_block
from ..events import EventBus


@runtime_checkable
class ConfirmerProtocol(Protocol):
    def ask(self, action: str, preview: Any) -> bool: ...


@dataclass
class ToolContext:
    cfg: AgentConfig
    bus: EventBus
    confirm: ConfirmerProtocol
    depth: int
    workdir: Path


@dataclass
class ToolResult:
    content: str
    is_error: bool = False

    def to_block(self, tool_use_id: str) -> dict[str, Any]:
        return tool_result_block(tool_use_id, self.content, self.is_error)


class Tool(ABC):
    name: str = ""
    description: str = ""
    input_schema: dict[str, Any] = {}
    destructive: bool = False

    @abstractmethod
    def run(self, tool_input: dict[str, Any], ctx: ToolContext) -> ToolResult: ...

    def preview(self, tool_input: dict[str, Any]) -> Any:
        """A renderable shown before confirmation. Overridden by destructive tools."""
        import json

        try:
            return json.dumps(tool_input, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(tool_input)

    def to_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    def __init__(self, tools: list[Tool]) -> None:
        self._tools: dict[str, Tool] = {t.name: t for t in tools}

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def schemas(self) -> list[dict[str, Any]]:
        return [t.to_schema() for t in self._tools.values()]

    def names(self) -> list[str]:
        return list(self._tools)
