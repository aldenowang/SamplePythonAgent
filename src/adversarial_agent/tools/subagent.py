"""spawn_subagent tool (architecture.md section 10).

Delegates a scoped task to a fresh AgentRunner at depth+1 that shares the same
event bus and Confirmer but gets a restricted registry (no nested delegation).
Only the child's final summary crosses back to the parent.
"""

from __future__ import annotations

from typing import Any

from ..events import Event, EventType
from .base import Tool, ToolContext, ToolResult


class SpawnSubagentTool(Tool):
    name = "spawn_subagent"
    description = (
        "Delegate a focused, self-contained subtask to a sub-agent. Provide a "
        "clear 'task' (and optional 'context'). The sub-agent has file and bash "
        "tools but cannot spawn further sub-agents. Returns its final summary."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "The subtask to perform."},
            "context": {"type": "string", "description": "Optional extra context."},
        },
        "required": ["task"],
        "additionalProperties": False,
    }
    destructive = False  # the child's own destructive steps are confirmed individually

    def run(self, tool_input: dict[str, Any], ctx: ToolContext) -> ToolResult:
        # Lazy imports avoid an import cycle (runner -> tools -> subagent -> runner).
        from ..conversation import Conversation
        from ..llm import LLMClient
        from ..prompts import subagent_system_prompt
        from ..runner import AgentRunner
        from . import build_registry

        if ctx.depth >= ctx.cfg.max_subagent_depth:
            return ToolResult(
                "Error: sub-agent depth limit reached; cannot spawn another.",
                is_error=True,
            )

        task = tool_input.get("task", "")
        extra = tool_input.get("context")
        seed = task if not extra else f"{task}\n\nContext:\n{extra}"

        ctx.bus.emit(Event(EventType.SUBAGENT_START, ctx.depth, {"task": task}))

        child = AgentRunner(
            cfg=ctx.cfg,
            bus=ctx.bus,
            llm=LLMClient(ctx.cfg),
            system_prompt=subagent_system_prompt(str(ctx.workdir)),
            registry=build_registry(allow_subagent=False),
            confirmer=ctx.confirm,
            workdir=ctx.workdir,
            depth=ctx.depth + 1,
            conversation=Conversation(),
        )
        summary = child.run_turn(seed)

        ctx.bus.emit(Event(EventType.SUBAGENT_STOP, ctx.depth, {"summary": summary}))
        return ToolResult(summary)
