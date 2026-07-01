"""In-memory conversation history (architecture.md section 7).

Stores API-shaped messages. Assistant turns are stored *verbatim* (the raw
content blocks returned by the API) so that thinking blocks and their
signatures are preserved when replayed alongside tool results (rules R4/R5).
History is in-memory only and not persisted (NFR-7).
"""

from __future__ import annotations

from typing import Any


class Conversation:
    def __init__(self) -> None:
        self._messages: list[dict[str, Any]] = []

    def add_user_text(self, text: str) -> None:
        self._messages.append(
            {"role": "user", "content": [{"type": "text", "text": text}]}
        )

    def add_assistant_blocks(self, blocks: Any) -> None:
        """Append the assistant response content list unchanged (R4/R5)."""
        self._messages.append({"role": "assistant", "content": blocks})

    def add_tool_results(self, results: list[dict[str, Any]]) -> None:
        """Append one user message carrying all tool_result blocks for the turn."""
        self._messages.append({"role": "user", "content": results})

    def to_api(self) -> list[dict[str, Any]]:
        return self._messages

    def __len__(self) -> int:
        return len(self._messages)


def tool_result_block(tool_use_id: str, content: str, is_error: bool = False) -> dict[str, Any]:
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": content,
        "is_error": is_error,
    }
