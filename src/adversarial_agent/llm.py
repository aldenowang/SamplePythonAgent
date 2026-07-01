"""Thin wrapper around the Anthropic Messages API.

See architecture.md section 6. Encapsulates the extended-thinking + tool-use
request so the hard rules are enforced in one place:

  R1  tool_choice must be {"type": "auto"} (forced tool use breaks thinking)
  R2  thinking.display = "summarized" so the trace is visible
  R3  no temperature / top_p / top_k when thinking is enabled
  R6  thinking budget_tokens >= 1024 and < max_tokens (validated in config)

Preserving thinking blocks (R4/R5) is the Conversation's responsibility.
"""

from __future__ import annotations

from typing import Any

import anthropic

from .config import AgentConfig


def build_request_kwargs(
    cfg: AgentConfig,
    messages: list[dict[str, Any]],
    tool_schemas: list[dict[str, Any]],
    system_prompt: str,
) -> dict[str, Any]:
    """Build kwargs for ``client.messages.create`` enforcing the hard rules."""
    kwargs: dict[str, Any] = {
        "model": cfg.model,
        "max_tokens": cfg.max_tokens,
        "system": system_prompt,
        "thinking": {
            "type": "enabled",
            "budget_tokens": cfg.thinking_budget,
            "display": cfg.thinking_display,  # R2: never "omitted"
        },
        "messages": messages,
        # R3: deliberately NO temperature / top_p / top_k.
    }
    if tool_schemas:
        kwargs["tools"] = tool_schemas
        kwargs["tool_choice"] = {"type": "auto"}  # R1
    return kwargs


class LLMClient:
    def __init__(self, cfg: AgentConfig, client: Any | None = None) -> None:
        self.cfg = cfg
        self.client = client or anthropic.Anthropic(api_key=cfg.api_key)

    def create(
        self,
        messages: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
        system_prompt: str,
    ) -> Any:
        kwargs = build_request_kwargs(self.cfg, messages, tool_schemas, system_prompt)
        return self.client.messages.create(**kwargs)
