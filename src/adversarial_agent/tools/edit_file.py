"""edit_file tool (architecture.md section 9.2). Destructive: requires confirm.

Exact-string replacement with Cursor/Claude-style semantics: old_string must be
present, and unique unless replace_all is true.
"""

from __future__ import annotations

import difflib
from typing import Any

from rich.syntax import Syntax

from .base import Tool, ToolContext, ToolResult


class EditFileTool(Tool):
    name = "edit_file"
    description = (
        "Replace an exact substring in a file. 'old_string' must match exactly and "
        "be unique unless 'replace_all' is true. Use this for targeted edits."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to edit."},
            "old_string": {"type": "string", "description": "Exact text to replace."},
            "new_string": {"type": "string", "description": "Replacement text."},
            "replace_all": {"type": "boolean", "default": False},
        },
        "required": ["path", "old_string", "new_string"],
        "additionalProperties": False,
    }
    destructive = True

    def preview(self, tool_input: dict[str, Any]) -> Any:
        path = tool_input.get("path", "")
        old = tool_input.get("old_string", "")
        new = tool_input.get("new_string", "")
        diff = difflib.unified_diff(
            old.splitlines(), new.splitlines(),
            fromfile=f"{path} (old)", tofile=f"{path} (new)", lineterm="",
        )
        diff_text = "\n".join(diff) or "(no textual difference)"
        return Syntax(diff_text, "diff", line_numbers=False, word_wrap=True)

    def run(self, tool_input: dict[str, Any], ctx: ToolContext) -> ToolResult:
        raw_path = tool_input.get("path", "")
        old = tool_input.get("old_string", "")
        new = tool_input.get("new_string", "")
        replace_all = bool(tool_input.get("replace_all", False))

        path = (ctx.workdir / raw_path).resolve()
        if not path.exists() or path.is_dir():
            return ToolResult(f"Error: file not found: {raw_path}", is_error=True)

        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count == 0:
            return ToolResult(
                f"Error: old_string not found in {raw_path}.", is_error=True
            )
        if count > 1 and not replace_all:
            return ToolResult(
                f"Error: old_string is not unique in {raw_path} "
                f"({count} matches). Pass replace_all=true to replace all.",
                is_error=True,
            )

        updated = text.replace(old, new) if replace_all else text.replace(old, new, 1)
        path.write_text(updated, encoding="utf-8")
        replaced = count if replace_all else 1
        return ToolResult(f"Edited {raw_path} ({replaced} replacement(s))")
