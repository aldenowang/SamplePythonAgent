"""Entry point for the minimal terminal coding agent.

Builds the event bus, subscribes the console renderer, constructs the agent
runner, and runs the REPL.
"""

from __future__ import annotations

import os

from rich.panel import Panel

from pathlib import Path

import anthropic

from .config import ConfigError, load_config
from .conversation import Conversation
from .events import Event, EventBus, EventType
from .llm import LLMClient
from .prompts import main_system_prompt
from .runner import AgentRunner
from .tools import build_registry
from .ui.confirm import Confirmer
from .ui.console import console
from .ui.renderer import ConsoleRenderer

EXIT_COMMANDS = {"exit", "quit", ":q"}


def banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]mini coding agent[/bold cyan]\n"
            "[dim]a terminal coding agent - teaching build[/dim]\n"
            "[dim]type 'exit' to quit[/dim]",
            border_style="cyan",
        )
    )


def repl(runner: AgentRunner) -> None:
    banner()
    while True:
        try:
            user_input = console.input("[bold green]> [/bold green]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]bye[/dim]")
            return
        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            console.print("[dim]bye[/dim]")
            return
        try:
            runner.run_turn(user_input)
        except KeyboardInterrupt:
            console.print("\n[yellow]turn cancelled[/yellow]")
        except anthropic.APIError as exc:
            runner.bus.emit(Event(EventType.ERROR, 0, {"message": f"API error: {exc}"}))
        except Exception as exc:  # keep the session alive on unexpected errors
            runner.bus.emit(
                Event(EventType.ERROR, 0, {"message": f"{type(exc).__name__}: {exc}"})
            )


def main() -> None:
    try:
        cfg = load_config()
    except ConfigError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise SystemExit(1)

    bus = EventBus()
    bus.subscribe(ConsoleRenderer(console))
    if cfg.transcript:
        from .ui.transcript import TranscriptListener

        bus.subscribe(TranscriptListener("agent_transcript.jsonl"))

    workdir = Path(os.getcwd())
    runner = AgentRunner(
        cfg=cfg,
        bus=bus,
        llm=LLMClient(cfg),
        system_prompt=main_system_prompt(str(workdir)),
        registry=build_registry(),
        confirmer=Confirmer(),
        workdir=workdir,
        conversation=Conversation(),
    )
    repl(runner)


if __name__ == "__main__":
    main()
