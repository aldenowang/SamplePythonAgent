"""Tool framework and built-in tools for the coding agent."""

from __future__ import annotations

from .base import Tool, ToolContext, ToolRegistry, ToolResult
from .bash import BashTool
from .edit_file import EditFileTool
from .read_file import ReadFileTool
from .write_file import WriteFileTool

__all__ = [
    "Tool",
    "ToolContext",
    "ToolRegistry",
    "ToolResult",
    "build_registry",
]


def build_registry(allow_subagent: bool = True) -> ToolRegistry:
    """Construct the tool registry.

    ``allow_subagent`` lets sub-agents receive a restricted registry (no nested
    delegation). The spawn_subagent tool is added in build task T16.
    """
    tools: list[Tool] = [
        ReadFileTool(),
        WriteFileTool(),
        EditFileTool(),
        BashTool(),
    ]
    if allow_subagent:
        from .subagent import SpawnSubagentTool

        tools.append(SpawnSubagentTool())
    return ToolRegistry(tools)
