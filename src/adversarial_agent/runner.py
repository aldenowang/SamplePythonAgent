"""AgentRunner: the core agent loop (architecture.md section 8).

The runner emits events to the bus instead of rendering directly, runs the
tool-use loop, and gates destructive tools through the Confirmer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .conversation import Conversation
from .events import Event, EventBus, EventType
from .llm import LLMClient
from .tools.base import ToolContext, ToolRegistry, ToolResult

MAX_ITERATIONS = 50


def block_type(block: Any) -> str | None:
    if isinstance(block, dict):
        return block.get("type")
    return getattr(block, "type", None)


def block_attr(block: Any, name: str) -> Any:
    if isinstance(block, dict):
        return block.get(name)
    return getattr(block, name, None)


def last_text(content: Any) -> str:
    texts = [block_attr(b, "text") or "" for b in content if block_type(b) == "text"]
    return "\n".join(t for t in texts if t).strip()


class AgentRunner:
    def __init__(
        self,
        cfg: Any,
        bus: EventBus,
        llm: LLMClient,
        system_prompt: str,
        registry: ToolRegistry | None = None,
        confirmer: Any = None,
        workdir: Path | None = None,
        depth: int = 0,
        conversation: Conversation | None = None,
    ) -> None:
        self.cfg = cfg
        self.bus = bus
        self.llm = llm
        self.system_prompt = system_prompt
        self.registry = registry
        self.confirmer = confirmer
        self.workdir = workdir or Path.cwd()
        self.depth = depth
        self.conversation = conversation or Conversation()
        self.tool_schemas: list[dict[str, Any]] = registry.schemas() if registry else []

    def run_turn(self, user_input: str) -> str:
        self.bus.emit(Event(EventType.USER_INPUT, self.depth, {"text": user_input}))
        self.conversation.add_user_text(user_input)

        for _ in range(MAX_ITERATIONS):
            resp = self.llm.create(
                self.conversation.to_api(), self.tool_schemas, self.system_prompt
            )
            content = resp.content

            for block in content:
                btype = block_type(block)
                if btype == "thinking":
                    self.bus.emit(
                        Event(EventType.THINKING, self.depth, {"text": block_attr(block, "thinking")})
                    )
                elif btype == "text":
                    self.bus.emit(
                        Event(EventType.AGENT_TEXT, self.depth, {"text": block_attr(block, "text")})
                    )

            self.conversation.add_assistant_blocks(content)

            if getattr(resp, "stop_reason", None) != "tool_use":
                final = last_text(content)
                if self.depth == 0:
                    self.bus.emit(Event(EventType.STOP, self.depth, {"text": final}))
                return final

            tool_results = []
            for block in content:
                if block_type(block) == "tool_use":
                    result = self.dispatch_tool(block)
                    tool_results.append(result.to_block(block_attr(block, "id")))
            self.conversation.add_tool_results(tool_results)

        self.bus.emit(
            Event(EventType.NOTICE, self.depth, {"message": "Max iterations reached."})
        )
        return "Stopped: reached the per-turn tool iteration limit."

    def dispatch_tool(self, block: Any) -> ToolResult:
        name = block_attr(block, "name")
        tool_input = block_attr(block, "input") or {}
        tool_use_id = block_attr(block, "id")

        self.bus.emit(
            Event(
                EventType.PRE_TOOL_USE,
                self.depth,
                {"name": name, "input": tool_input, "tool_use_id": tool_use_id},
            )
        )

        tool = self.registry.get(name) if self.registry else None
        if tool is None:
            return self._finish_tool(name, tool_use_id, ToolResult(f"Error: unknown tool '{name}'", is_error=True))

        if tool.destructive:
            preview = tool.preview(tool_input)
            approved = self.confirmer.ask(name, preview) if self.confirmer else True
            if not approved:
                return self._finish_tool(
                    name,
                    tool_use_id,
                    ToolResult(f"User declined to run '{name}'."),
                )

        ctx = ToolContext(
            cfg=self.cfg,
            bus=self.bus,
            confirm=self.confirmer,
            depth=self.depth,
            workdir=self.workdir,
        )
        try:
            result = tool.run(tool_input, ctx)
        except Exception as exc:  # tool errors are model-visible, not fatal
            result = ToolResult(f"Error: {type(exc).__name__}: {exc}", is_error=True)

        result.content = _truncate(result.content, self.cfg.max_tool_output_chars)
        return self._finish_tool(name, tool_use_id, result)

    def _finish_tool(self, name: str, tool_use_id: str, result: ToolResult) -> ToolResult:
        self.bus.emit(
            Event(
                EventType.POST_TOOL_USE,
                self.depth,
                {
                    "name": name,
                    "tool_use_id": tool_use_id,
                    "content": result.content,
                    "is_error": result.is_error,
                },
            )
        )
        return result


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated {len(text) - limit} chars]"
