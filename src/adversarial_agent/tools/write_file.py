"""write_file tool (architecture.md section 9.2). Destructive: requires confirm."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Group
from rich.syntax import Syntax
from rich.text import Text

from .base import Tool, ToolContext, ToolResult


class WriteFileTool(Tool):
    name = "write_file"
    description = (
        "Create a new file or overwrite an existing one with the given content. "
        "Parent directories are created as needed."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write."},
            "content": {"type": "string", "description": "Full file content."},
        },
        "required": ["path", "content"],
        "additionalProperties": False,
    }
    destructive = True

    def preview(self, tool_input: dict[str, Any]) -> Any:
        path = tool_input.get("path", "")
        content = tool_input.get("content", "")
        lexer = Syntax.guess_lexer(path, content)
        header = Text.assemble(("write ", "bold"), (path, "cyan"))
        body = Syntax(content, lexer, line_numbers=False, word_wrap=True)
        return Group(header, body)

    def run(self, tool_input: dict[str, Any], ctx: ToolContext) -> ToolResult:
        raw_path = tool_input.get("path", "")
        content = tool_input.get("content", "")
        path = (ctx.workdir / raw_path).resolve()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = content.encode("utf-8")
            path.write_bytes(data)
        except OSError as exc:
            return ToolResult(f"Error writing {raw_path}: {exc}", is_error=True)
        return ToolResult(f"Wrote {len(data)} bytes to {raw_path}")
