# Backend — AI Software Engineer Agent

FastAPI + LangGraph backend that drives the Plan → Code → Execute → Debug
loop against local Ollama models.

## 1. Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running (`ollama serve`, or
  just launch the desktop app)

Docker is **not required**. Code runs via `SubprocessExecutor` by default —
directly on this machine, no container involved. A sandboxed `DockerExecutor`
is still included and fully working if you want real isolation later; see
"Switching to the Docker sandbox" below. Nothing else changes if you do.

## 2. First-time setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows (PowerShell): .venv\Scripts\Activate.ps1
                                     # Windows (cmd.exe):    .venv\Scripts\activate.bat

pip install -r requirements.txt

cp .env.example .env                # defaults are sane; edit if you want different models

# Pull the three models this project routes to by default (~15-20GB total;
# adjust the tags in .env first if you want smaller/different models)
ollama pull llama3:8b
ollama pull qwen2.5-coder:7b
ollama pull codellama:13b-instruct
```

## 3. Run it

```bash
uvicorn app.main:app --reload --port 8000
```

Check `http://localhost:8000/health` — it should report
`"ollama_reachable": true` and an empty `"missing_models"` list. If a model
is missing, either `ollama pull` it manually or `POST /api/models/pull` to
have the server pull it for you (streams progress to the server console).

### Try it without the frontend

```bash
# in a second terminal, same venv
python scripts/test_client.py "write a function that checks if a number is prime, then test it on 2..50"
```

You'll see the Planner's plan, the Coder's script, stdout/stderr, and — if
the first attempt fails — the Reviewer's diagnosis followed by a corrected
script, streamed as they happen.

## 4. Run the test suite

```bash
pip install -r requirements-dev.txt
pytest -v
```

`tests/test_graph_smoke.py` runs the *entire* graph — including the
debug/retry loop and the environment-error short-circuit — against scripted
fake LLM responses and `SubprocessExecutor`, so it passes with no Ollama
running at all. It's there to catch regressions in the graph wiring itself,
separate from whatever a real model happens to output.

## Configuration reference

Every setting lives in `app/config.py` and can be overridden via `.env` —
see `.env.example` for the full list with defaults. The ones you're most
likely to touch:

| Variable | Default | Purpose |
|---|---|---|
| `PLANNER_MODEL` / `CODER_MODEL` / `REVIEWER_MODEL` | `llama3:8b` / `qwen2.5-coder:7b` / `codellama:13b-instruct` | Which Ollama tag each role uses |
| `MAX_DEBUG_ITERATIONS` | `4` | How many reviewer→coder cycles before giving up |
| `EXECUTOR_BACKEND` | `subprocess` | `subprocess` (host, no Docker needed) or `docker` (sandboxed) |
| `SANDBOX_TIMEOUT_SECONDS` | `20` | Wall-clock kill switch per execution |

### Swapping models

The defaults match the brief exactly. If your hardware can take something
newer/bigger, reasonable 2026-era upgrades for the same roles are
`qwen3-coder:30b` or `devstral:24b` for the Coder, and `llama3.3:70b` for the
Planner — just `ollama pull` the tag and set the matching env var, nothing
else changes.

## API surface

- `GET /health` — `{ollama_reachable, required_models, missing_models, executor_backend, max_debug_iterations}`
- `POST /api/models/pull` — pulls every configured model that's missing
- `WS /ws/agent` — send `{"task": "...", "max_iterations": 4}` (the second
  field is optional), receive a stream of events shaped like
  `app.schemas.AgentEvent`: `{type, agent, content, iteration, ts}`, always
  ending in a `{"type": "done", ...}` event regardless of how the run ended.
  Send another task on the same connection to start a second run without
  reconnecting.

## Switching to the Docker sandbox

`subprocess` shares your host's filesystem and network with whatever the
LLM wrote — fine for trying things out, not something to leave on
indefinitely. When you're ready for real isolation (network-disabled,
CPU/memory-capped, non-root, throwaway containers):

```bash
docker build -t agent-sandbox:latest -f Dockerfile.sandbox .
```

then set `EXECUTOR_BACKEND=docker` in `.env` and restart uvicorn. See
`app/sandbox/docker_executor.py` for exactly what's isolated and why.

## Extending

- **Multi-file projects**: the Coder currently targets a single script
  (`solution.py`). To support whole projects, change `AgentState.code` to a
  `dict[str, str]` of `{filename: contents}`, have the Planner enumerate
  files, and mount all of them into the sandbox workspace.
- **Real test execution**: the success heuristic in `executor_node`
  (`nodes.py`) is "exit code 0 and no visible traceback." For tasks that
  should be judged against actual test cases, have the Planner emit a
  pytest file alongside the solution and change the executor's command to
  `pytest`.
- **New sandbox packages** (Docker mode only): add to the `pip install`
  list in `Dockerfile.sandbox` and rebuild the image — the network-disabled
  container can't install anything at run time by design.

## Troubleshooting

**A task seems to hang with nothing happening** — check `/health` first;
the most common cause is Ollama not running, or a model that isn't pulled
yet. The frontend's health banner (once you're running it) surfaces this
automatically.

**Switched to `EXECUTOR_BACKEND=docker` and `stderr` says "Could not reach
the Docker daemon"** — Docker Desktop isn't running (or isn't installed).
This is reported as a distinct `environment_error` state, not a code
failure: the graph short-circuits immediately instead of sending the
Reviewer a Docker connection error to "diagnose" as if it were a Python bug
(it used to do exactly that before this was fixed — see
`tests/test_graph_smoke.py::test_environment_error_short_circuits_without_touching_the_reviewer`
for the regression test). Start Docker Desktop and build the sandbox image,
or switch `EXECUTOR_BACKEND` back to `subprocess`.

**On Windows**, "installed" and "running" are different things for Docker —
Desktop has to actually be open (check the system tray) before
`docker.from_env()` can reach it; a fresh install doesn't start it
automatically.
