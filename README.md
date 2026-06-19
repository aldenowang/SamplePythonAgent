# mini coding agent

A minimal, terminal-based coding agent — a "mini Claude Code" — built in Python
on the Anthropic API. It reads/writes/edits files, runs bash commands, and can
delegate subtasks to sub-agents. Its **extended-thinking trace** and **tool
calls** are surfaced live in a `rich` terminal UI.

This project is intentionally simple and readable: it's meant as a **teaching
reference** for how a coding agent works end to end. See `architecture.md` for
the full design and `tasks.md` for the build breakdown.

## Features

- Interactive terminal REPL with a polished `rich` UI.
- Extended thinking rendered as a visible "thinking" trace.
- Five tools: `read_file`, `write_file`, `edit_file`, `bash`, `spawn_subagent`.
- Confirmation prompts before any destructive action (write/edit/bash).
- Event-driven core: the agent emits events; the UI (and an optional transcript
  logger) are listeners. Lifecycle events mirror Claude Code's hooks
  (`PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`).

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"   # or: pip install -r requirements.txt
```

Then configure your API key:

```bash
copy .env.example .env    # Windows  (cp .env.example .env on macOS/Linux)
# edit .env and set ANTHROPIC_API_KEY=...
```

Environment variables (see `.env.example`):

- `ANTHROPIC_API_KEY` (required) — your Anthropic API key.
- `ANTHROPIC_MODEL` (optional) — override the default model (`claude-opus-4-8`).
- `AGENT_TRANSCRIPT` (optional) — set to `1` to also write
  `agent_transcript.jsonl`, one JSON record per event.

## Run

```bash
python -m cmu_project.main
```

Type instructions at the `>` prompt. Type `exit` (or `quit`) to leave.

### Sample session

```
> add a function `add(a, b)` to calc.py and run it

  thinking  I'll create calc.py with an add function, then run it.
  -> write_file   { "path": "calc.py", ... }
  confirm: write_file   [y/n/a]  y
  <- write_file   Wrote 48 bytes to calc.py
  -> bash         { "command": "python -c \"import calc; print(calc.add(2,3))\"" }
  confirm: bash   [y/n/a]  y
  <- bash         exit=0  5
  Done — calc.py has add(a, b); add(2, 3) returned 5.
```

## Run with Docker

The container doubles as a **sandbox**: the agent's file writes and shell
commands stay inside the container, operating on whatever you mount at
`/workspace`. Your API key is passed at runtime and never baked into the image.

The image is built from the published repo
(`github.com/aldenowang/SamplePythonAgent`); it clones and installs the package
at build time. Build the image:

```bash
docker build -t mini-coding-agent .

# Pin a specific branch or tag:
docker build --build-arg AGENT_REF=main -t mini-coding-agent .
```

Run it interactively (mount the directory you want the agent to work on):

```bash
# macOS/Linux
docker run -it --rm --env-file .env -v "$PWD/workspace:/workspace" mini-coding-agent

# Windows PowerShell
docker run -it --rm --env-file .env -v "${PWD}\workspace:/workspace" mini-coding-agent
```

Or use Docker Compose (note `run`, not `up`, so you get an interactive TTY):

```bash
docker compose run --rm agent
```

The `-it` flags / `stdin_open` + `tty` are required because the REPL and the
confirmation prompts read from the terminal.

## Test

```bash
pytest
```

Tests run fully offline (the Anthropic client is mocked).

## Architecture (quick tour)

```
src/cmu_project/
  main.py          REPL: builds the bus, renderer, runner
  config.py        AgentConfig + env loading
  events.py        EventBus, Event, EventType (Claude Code lifecycle names)
  llm.py           Anthropic wrapper (extended thinking + tool use rules)
  conversation.py  in-memory, thinking-block-preserving history
  runner.py        the agent loop: emits events, dispatches tools
  prompts.py       system prompts (main + sub-agent)
  tools/           read_file, write_file, edit_file, bash, spawn_subagent
  ui/              console, renderer (listener), confirm, transcript (listener)
```

The core (`runner`, `tools`) emits events and never imports the UI; the UI
subscribes to the bus. See `architecture.md` for the full rationale, the
extended-thinking + tool-use API rules, and the decision log.

## Safety / sandbox warning

This agent **executes model-decided file writes and shell commands on your
machine**. Mitigations: every destructive action requires confirmation, bash
runs with a timeout, and previews show exactly what will happen. It is **not
sandboxed**. Run it only in a directory/repository you trust — ideally inside a
disposable VM or container when experimenting.
