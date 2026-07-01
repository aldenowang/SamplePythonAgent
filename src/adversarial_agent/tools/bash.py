"""bash tool (architecture.md section 9.2). Destructive: requires confirm."""

from __future__ import annotations

import subprocess
from typing import Any

from rich.syntax import Syntax

from .base import Tool, ToolContext, ToolResult


class BashTool(Tool):
    name = "bash"
    description = (
        "Run a shell command in the working directory and return its combined "
        "stdout/stderr and exit code. Use for builds, tests, git, and inspection."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The shell command to run."},
        },
        "required": ["command"],
        "additionalProperties": False,
    }
    destructive = True

    def preview(self, tool_input: dict[str, Any]) -> Any:
        command = tool_input.get("command", "")
        return Syntax(command, "bash", line_numbers=False, word_wrap=True)

    def run(self, tool_input: dict[str, Any], ctx: ToolContext) -> ToolResult:
        command = tool_input.get("command", "")
        if not command.strip():
            return ToolResult("Error: empty command.", is_error=True)
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(ctx.workdir),
                capture_output=True,
                text=True,
                timeout=ctx.cfg.bash_timeout_s,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                f"Error: command timed out after {ctx.cfg.bash_timeout_s}s.",
                is_error=True,
            )
        output = (proc.stdout or "") + (proc.stderr or "")
        body = f"exit={proc.returncode}\n{output}".rstrip()
        return ToolResult(body, is_error=proc.returncode != 0)
