# AI Software Engineer Agent

A fully local, autonomous coding agent: describe what you want built, and a
closed loop of local LLMs (served by [Ollama](https://ollama.com)) plans it,
writes it, runs it in a sandboxed Docker container, and rewrites it against
real tracebacks until it works — no external API keys, no data leaving your
machine.

## Status

**This covers backend + agent loop (steps 1–2 of the build).** The React
frontend and the unified run instructions (steps 3–4) land next — see
`backend/README.md` for how to exercise everything already built via a
one-line test client in the meantime.

## Architecture

```
┌─────────────┐      ┌──────────────────────────────────────────────────┐
│   React UI   │◄────►│                FastAPI backend                   │
│ (next step)  │  WS  │                                                    │
└─────────────┘      │   ┌────────┐   ┌───────┐   ┌──────────┐          │
                     │   │Planner │──►│ Coder │──►│ Executor  │          │
                     │   │(llama3)│   │(qwen2.5│   │ (Docker   │          │
                     │   └────────┘   │ -coder)│   │ sandbox)  │          │
                     │                └───▲────┘   └────┬─────┘          │
                     │                    │              │ pass/fail      │
                     │              ┌─────┴──────┐       │                │
                     │              │  Reviewer   │◄──────┘                │
                     │              │(codellama)  │                        │
                     │              └─────────────┘                        │
                     │        LangGraph state machine, all local models    │
                     └──────────────────────────────────────────────────┘
                                          │
                                    Ollama (localhost:11434)
```

Each role — Planner, Coder, Reviewer — is routed to its own local model via
`backend/app/llm/router.py`, matching the brief's table:

| Role | Default model | Job |
|---|---|---|
| Planner | `llama3:8b` | Break the request into a concrete plan + dependency list |
| Coder | `qwen2.5-coder:7b` | Write (and rewrite) the actual script |
| Reviewer | `codellama:13b-instruct` | Diagnose failures, hand fix instructions back to the Coder |

The loop itself is a `LangGraph` `StateGraph`:
`planner → coder → executor →` (success → done) or (failure → `reviewer` →
back to `coder`, up to `MAX_DEBUG_ITERATIONS` times).

## Repo layout

```
ai-swe-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app: /health, /api/models/pull, /ws/agent
│   │   ├── config.py             every tunable, env-var driven
│   │   ├── schemas.py            wire-format Pydantic models
│   │   ├── llm/
│   │   │   ├── router.py         agent role -> ChatOllama instance
│   │   │   └── ollama_admin.py   health check + model pulling
│   │   ├── agents/
│   │   │   ├── state.py          LangGraph shared state
│   │   │   ├── prompts.py        system prompts per role
│   │   │   ├── nodes.py          Planner/Coder/Executor/Reviewer node functions
│   │   │   └── graph.py          the state machine wiring
│   │   └── sandbox/
│   │       ├── docker_executor.py       sandboxed execution (recommended)
│   │       ├── subprocess_executor.py   unsandboxed fallback for local dev
│   │       └── factory.py               picks one based on EXECUTOR_BACKEND
│   ├── tests/                    pytest suite, including a full-loop smoke test
│   ├── scripts/test_client.py    exercise the WebSocket without a frontend
│   ├── Dockerfile.sandbox        the image generated code actually runs inside
│   ├── requirements.txt
│   └── README.md                 full setup + run instructions
└── README.md                     you are here
```

## Quickstart (backend only, for now)

```bash
# 1. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Models (adjust tags in .env first if you want different ones)
ollama pull llama3:8b
ollama pull qwen2.5-coder:7b
ollama pull codellama:13b-instruct

# 3. Sandbox image
docker build -t agent-sandbox:latest -f Dockerfile.sandbox .

# 4. Run
uvicorn app.main:app --reload --port 8000
```

Then, in a second terminal:

```bash
python scripts/test_client.py "write a function that checks if a number is prime, then test it on 2..50"
```

Full details, config reference, and extension notes are in
[`backend/README.md`](./backend/README.md).

## What's next

- **Frontend**: Vite + React + TypeScript + Tailwind, chat panel on the left,
  live code/terminal view on the right, wired to `/ws/agent`.
- **Unified run instructions**: one set of commands to bring up Ollama, the
  backend, and the frontend together.
