"""Shared test helpers: scripted fake LLM, block builders, recording listener."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any


def thinking(text: str) -> Any:
    return SimpleNamespace(type="thinking", thinking=text)


def text_block(text: str) -> Any:
    return SimpleNamespace(type="text", text=text)


def tool_use(block_id: str, name: str, tool_input: dict) -> Any:
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=tool_input)


def response(content: list, stop_reason: str) -> Any:
    return SimpleNamespace(content=content, stop_reason=stop_reason)


class ScriptedLLM:
    """Duck-types LLMClient.create by returning queued responses in order."""

    def __init__(self, responses: list) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    def create(self, messages, tool_schemas, system_prompt):
        self.calls.append(
            {"messages": messages, "tool_schemas": tool_schemas, "system": system_prompt}
        )
        return self._responses.pop(0)


class RecordingListener:
    def __init__(self) -> None:
        self.events: list = []

    def on_event(self, event) -> None:
        self.events.append(event)

    def types(self) -> list:
        return [e.type for e in self.events]
