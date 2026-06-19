# Requirements: Minimal Terminal Coding Agent

## 1. Overview

A terminal-based, minimal coding agent — a "mini ClaudeCode" — built in Python using the Anthropic API. The agent runs in the terminal, can read/write/edit files and execute bash commands, and exposes its thinking trace and tool calls so the user can follow what it is doing.

The project's primary purpose is **educational**: to teach developers how to build a coding agent from scratch. Implementation should therefore favor simplicity and readability over feature completeness.

## 2. Goals

- Provide a working, end-to-end coding agent that runs entirely in the terminal.
- Keep the implementation simple enough to serve as a learning reference.
- Make the agent's reasoning ("thinking trace") and tool usage visible and easy to follow.
- Offer a clean, attractive terminal UI.

## 3. Non-Goals (initial build)

- Response streaming (explicitly out of scope for v1).
- Advanced agent capabilities beyond core file + shell operations.
- Production-grade robustness, multi-user support, or deployment concerns.

## 4. Target User

A **developer learning how to build coding agents from scratch**. The user values clear, understandable code and an observable agent loop more than a large feature set.

## 5. Functional Requirements

### 5.1 Agent Core
- FR-1: Start an interactive session from the terminal.
- FR-2: Accept natural-language instructions from the user in a conversational loop.
- FR-3: Use the Anthropic API to drive reasoning and tool selection.
- FR-4: Support multi-step tool use (the agent can call tools, observe results, and continue).

### 5.2 Tools
- FR-5: **Read file** — read the contents of a file.
- FR-6: **Write file** — create or overwrite a file.
- FR-7: **Edit file** — modify an existing file.
- FR-8: **Execute bash command** — run shell commands and capture output.
- FR-9: **Spawn sub-agent** — delegate a scoped task to a sub-agent that runs its own tool-use loop and returns a result/summary to the main agent. Useful for breaking a larger task into an isolated, focused unit of work.

### 5.3 Observability (high priority)
- FR-10: Display the agent's **thinking trace** in the terminal (rendered from the model's extended-thinking blocks).
- FR-11: Display each **tool call** being made, including which tool and its inputs.
- FR-12: Display tool results / outputs back in the terminal.
- FR-13: Make **sub-agent activity** visible — show when a sub-agent is spawned, its task, and its returned result (and ideally its own thinking/tool calls, visually nested/distinguished from the main agent).

### 5.4 Terminal UI
- FR-14: Provide a clean, nice-looking text UI (intended to use the Python `rich` library).
- FR-15: Visually distinguish user input, agent thinking, tool calls, and tool results.

## 6. Non-Functional Requirements

- NFR-1: **Language/Stack** — Python + Anthropic API.
- NFR-2: **Simplicity** — code should be approachable and well-organized for learning.
- NFR-3: **No streaming** — responses are rendered after completion, not token-by-token.
- NFR-4: **UI quality** — terminal output should look polished (likely via `rich`).
- NFR-5: **Model** — default to Claude Opus.
- NFR-6: **Safety** — require explicit user confirmation before destructive actions (file writes, file edits, and bash command execution).
- NFR-7: **Memory** — conversation history is in-memory only; each run starts fresh (no cross-session persistence).

## 7. Resolved Design Decisions

- **Model:** Claude Opus is the default model.
- **Thinking trace:** Implemented via Anthropic's **extended thinking** feature — the agent's real reasoning (thinking blocks) is surfaced and rendered in the terminal before/between tool calls.
- **Confirmation flow:** The agent must prompt the user for approval before writing files, editing files, or running bash commands.
- **Conversation memory:** In-memory only; history is not saved or restored between sessions.
- **Tool set (v1):** Five tools — read file, write file, edit file, execute bash, and spawn sub-agent. (List-directory and search/grep are deferred.)

## 8. Open Questions

None outstanding — all initial scoping questions have been resolved (see Section 7).
