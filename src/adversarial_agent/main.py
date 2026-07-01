"""Entry point for the minimal terminal coding agent.
 
Builds the event bus, subscribes the console renderer, constructs the agent
runner, and runs the REPL.
 
EVAL MODE: pass a question as a command line argument to run a single turn
and print only the final numeric answer. Example:
    python -m adversarial_agent.main --eval "A gas has P=2 atm, V=10L, n=1mol. What is T in Kelvin?"
    python -m adversarial_agent.main --eval "question" transcripts/idealGasLaw_Q1.jsonl

    
"""

 
from __future__ import annotations
 
import os
import sys
 
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
 
"""
When you need to run Python code to compute an answer:
- Always use the write_file tool to save a .py file first
- Then run it with: python filename.py
- Never use heredocs (<< EOF or << 'PYEOF') — they do not work on Windows
- Never pipe through echo — it does not work reliably on Windows
"""
# --- EVAL MODE: system prompt for physics/math solving ---


EVAL_SYSTEM_PROMPT = """You are a physics and math problem solver running on Windows PowerShell.

Solve problems using only your own reasoning and calculations — do NOT use any tools, 
do NOT write Python files, do NOT run bash commands. Work through the math step by step 
in your head and compute the answer yourself.

At the very end of your response output ONLY the final numeric answer on its own line:

ANSWER: <number>

For example:
ANSWER: 243.6

Do not include units, text, or anything else on the ANSWER line — just the number.
If the answer is a list of indices (e.g. [2, 9]), output them comma-separated:
ANSWER: 2,9
"""
 
 
# --- EVAL MODE: auto-approving confirmer ---
class AutoConfirmer:
    """Approves all tool calls automatically — used in eval mode."""
    def ask(self, action: str, preview: object) -> bool:
        return True
 
 
# --- EVAL MODE: extract numeric answer from agent response ---
def extract_answer(text: str) -> str | None:
    """
    Look for a line starting with 'ANSWER:' and return the value after it.
    Returns None if not found.
    """
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("ANSWER:"):
            value = line[len("ANSWER:"):].strip()
            return value
    return None
 
 
# --- EVAL MODE: single-question entry point ---
def run_eval(question: str, transcript_path: str | None = None) -> None:
    """
    Run a single question through the agent and print only the numeric answer.
    Used by eval.py — no REPL, no banners, no rich formatting on the answer.
 
    If transcript_path is provided, logs all events (thinking, tool calls,
    tool results, final answer) to that JSONL file for later debugging.
    """
    try:
        cfg = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        raise SystemExit(1)
 
    bus = EventBus()
 
    # Subscribe transcript listener if path provided
    if transcript_path:
        from .ui.transcript import TranscriptListener
        p = Path(transcript_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            p.unlink()   # delete old file before writing new one
        bus.subscribe(TranscriptListener(transcript_path))
    
 
    workdir = Path(os.getcwd())
    runner = AgentRunner(
        cfg=cfg,
        bus=bus,
        llm=LLMClient(cfg),
        system_prompt=EVAL_SYSTEM_PROMPT,
        registry=build_registry(),
        confirmer=AutoConfirmer(),
        workdir=workdir,
        conversation=Conversation(),
    )
 
    final_text = runner.run_turn(question)
    answer = extract_answer(final_text)
 
    if answer is not None:
        print(answer)
    else:
        print(f"PARSE_ERROR: {final_text}", file=sys.stderr)
        raise SystemExit(1)
 
 
# --- EXISTING: banner and repl unchanged ---
 
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
        except Exception as exc:
            runner.bus.emit(
                Event(EventType.ERROR, 0, {"message": f"{type(exc).__name__}: {exc}"})
            )
 
 
def main() -> None:
    # detect eval mode — question is argv[2], optional transcript path is argv[3]
    if len(sys.argv) >= 3 and sys.argv[1] == "--eval":
        question = sys.argv[2]
        transcript_path = sys.argv[3] if len(sys.argv) >= 4 else None
        run_eval(question, transcript_path)
        return
 
    # normal REPL mode
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