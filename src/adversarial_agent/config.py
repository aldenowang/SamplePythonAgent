"""Configuration and environment loading.

See architecture.md section 5. Fails fast with a clear message when the API key
is missing or the thinking budget is misconfigured.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_MODEL = "claude-opus-4-8"


class ConfigError(RuntimeError):
    """Raised when the agent cannot be configured (e.g. missing API key)."""


@dataclass
class AgentConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    max_tokens: int = 8192
    thinking_budget: int = 4096  # must be >= 1024 and < max_tokens
    thinking_display: str = "summarized"  # must NOT be "omitted" (see architecture 6.2)
    max_subagent_depth: int = 1  # main = depth 0; sub-agents = depth 1
    bash_timeout_s: int = 120
    max_tool_output_chars: int = 20000
    transcript: bool = False  # when True, write a JSONL transcript of all events

    def validate(self) -> None:
        if not self.api_key:
            raise ConfigError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        if self.thinking_budget < 1024:
            raise ConfigError("thinking_budget must be >= 1024 tokens.")
        if self.thinking_budget >= self.max_tokens:
            raise ConfigError("thinking_budget must be strictly less than max_tokens.")
        if self.thinking_display == "omitted":
            raise ConfigError(
                'thinking_display must not be "omitted" or the thinking trace is hidden.'
            )


def load_config() -> AgentConfig:
    """Load configuration from the environment (and a local .env file)."""
    load_dotenv()
    cfg = AgentConfig(
        api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        model=os.environ.get("ANTHROPIC_MODEL", "").strip() or DEFAULT_MODEL,
        transcript=_truthy(os.environ.get("AGENT_TRANSCRIPT")),
    )
    cfg.validate()
    return cfg


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}
