"""read_file tool (architecture.md section 9.2). Non-destructive."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import Tool, ToolContext, ToolResult


class ReadFileTool(Tool):
    name = "read_file"
    description = (
        "Read a UTF-8 text file and return its contents with line numbers. "
        "Optionally read a slice using 1-indexed 'offset' and 'limit' (lines)."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to read."},
            "offset": {"type": "integer", "description": "1-indexed start line."},
            "limit": {"type": "integer", "description": "Max number of lines."},
        },
        "required": ["path"],
        "additionalProperties": False,
    }
    destructive = False

    def run(self, tool_input: dict[str, Any], ctx: ToolContext) -> ToolResult:
        raw_path = tool_input.get("path", "")
        path = (ctx.workdir / raw_path).resolve()
        if not path.exists():
            return ToolResult(f"Error: file not found: {raw_path}", is_error=True)
        if path.is_dir():
            return ToolResult(f"Error: path is a directory: {raw_path}", is_error=True)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(f"Error: not a UTF-8 text file: {raw_path}", is_error=True)

        lines = text.splitlines()
        offset = tool_input.get("offset")
        limit = tool_input.get("limit")
        start = (offset - 1) if isinstance(offset, int) and offset > 0 else 0
        end = (start + limit) if isinstance(limit, int) and limit > 0 else len(lines)
        selected = lines[start:end]

        numbered = "\n".join(
            f"{start + i + 1:6}| {line}" for i, line in enumerate(selected)
        )
        if not numbered:
            return ToolResult("(empty selection)")
        return ToolResult(numbered)
