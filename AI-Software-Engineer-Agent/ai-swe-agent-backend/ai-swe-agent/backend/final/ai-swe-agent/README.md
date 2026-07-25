# Agent Forge — a local AI software engineer

A fully local, autonomous coding agent: describe what you want built, and a
closed loop of local LLMs (served by [Ollama](https://ollama.com)) plans it,
writes it, runs it, and rewrites it against real tracebacks until it works —
no external API keys, no data leaving your machine.

## Status: complete

Backend (FastAPI + LangGraph), frontend (React + TypeScript + Tailwind), and
the run instructions below are all in place. Docker is available but
**optional** — everything defaults to running directly on your machine.

## Architecture

```
┌────────────────────┐      ┌──────────────────────────────────────────────┐
│   React frontend   │◄────►│               FastAPI backend                │
│  (chat + code/term)│  WS  │                                              │
└────────────────────┘      │   ┌────────┐   ┌───────┐   ┌───────────┐     │
                            │   │Planner │──►│ Coder │──►│ Executor  │     │
                            │   │(llama3)│   │(qwen2.5│  │(subprocess│     │
                            │   └────────┘   │ -coder)│  │by default)│     │
                            │                └───▲────┘  └─────┬─────┘     │
                            │                    │             │ pass/fail │
                            │              ┌─────┴──────┐      │           │
                            │              │  Reviewer   │◄────┘           │
                            │              │(codellama)  │                 │
                            │              └─────────────┘                 │
                            │   LangGraph state machine, all local models  │
                            └──────────────────────────────────────────────┘
                                                  │
                                       Ollama (localhost:11434)
```

Each role — Planner, Coder, Reviewer — is routed to its own local model via
`backend/app/llm/router.py`:

| Role | Default model | Job |
|---|---|---|
| Planner | `llama3:8b` | Break the request into a concrete plan + dependency list |
| Coder | `qwen2.5-coder:7b` | Write (and rewrite) the actual script |
| Reviewer | `codellama:13b-instruct` | Diagnose failures, hand fix instructions back to the Coder |

The loop is a `LangGraph` `StateGraph`: `planner → coder → executor →`
success (done), or a code failure with retries left (→ `reviewer` → back to
`coder`, up to `MAX_DEBUG_ITERATIONS` times), or an environment problem like
Docker being unreachable (→ an immediate, distinct failure state that never
wastes a debug cycle "fixing" code that was never actually broken).

## Repo layout

```
ai-swe-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                       FastAPI: /health, /api/models/pull, /ws/agent
│   │   ├── config.py                      every tunable, env-var driven
│   │   ├── llm/                           router.py (role -> ChatOllama), ollama_admin.py
│   │   ├── agents/                        state.py, prompts.py, nodes.py, graph.py
│   │   └── sandbox/                       docker_executor.py, subprocess_executor.py, factory.py
│   ├── tests/                             pytest suite incl. a full-loop smoke test
│   ├── scripts/test_client.py             exercise the WebSocket without a frontend
│   ├── Dockerfile.sandbox                 optional — only needed if you switch to Docker mode
│   └── README.md                          full backend setup + config reference
└── frontend/
    ├── src/
    │   ├── App.tsx                        layout: header, health banner, two panels
    │   ├── hooks/useAgentSocket.ts         WebSocket connection + derived UI state
    │   ├── hooks/useHealth.ts              polls /health
    │   └── components/                     EventFeed, WorkspacePanel, CodeView, TerminalView, ...
    └── README.md                           frontend setup + component overview
```

## Run everything

Three terminals: Ollama, backend, frontend.

**Terminal 1 — Ollama**

```bash
ollama serve
```

(Or just launch the Ollama desktop app — same effect.) Then, one-time, pull
the three models:

```bash
ollama pull llama3:8b
ollama pull qwen2.5-coder:7b
ollama pull codellama:13b-instruct
```

**Terminal 2 — Backend**

```powershell
# Windows (PowerShell)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

```bash
# macOS / Linux
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — Frontend**

```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173**. The header shows a green/red dot for
the WebSocket connection; the banner just below it tells you directly if
Ollama isn't reachable or a model is still missing, with the exact command
to fix it.

Type a task, hit **Build it** (or ⌘/Ctrl + Enter), and watch the Planner,
Coder, and Executor work through it in the left-hand timeline while the
right-hand panel shows the live code and terminal output.

## Switching to the Docker sandbox

Everything above runs generated code directly on your machine
(`SubprocessExecutor`) — no Docker needed. When you want real isolation
(network-disabled, resource-capped, non-root, throwaway containers), see
["Switching to the Docker sandbox"](./backend/README.md#switching-to-the-docker-sandbox)
in the backend README. It's a two-line change: build one image, flip one
env var.

## Verified, not just written

Both halves were actually built and run before being handed over, not just
generated and assumed to work:

- **Backend**: full `pip install` in a clean venv, all imports checked, and
  a pytest suite that runs the *entire* LangGraph loop — including the
  debug/retry cycle and the environment-error short-circuit — against
  scripted fake models, so it validates the graph wiring itself independent
  of what a real model outputs.
- **Frontend**: `tsc -b` (strict mode: `verbatimModuleSyntax`,
  `noUnusedLocals`, `erasableSyntaxOnly`) and `vite build` both pass clean,
  plus `oxlint` with zero warnings.
- **End-to-end**: the exact WebSocket contract the frontend consumes —
  including reusing one connection across multiple tasks, and a bad request
  correctly still receiving a `done` event — was integration-tested against
  the real FastAPI app with scripted models standing in for Ollama.
