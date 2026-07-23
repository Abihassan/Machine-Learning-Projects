# Multi-Agent Coding Sandbox

Four interdependent local-LLM agents (Product Manager, Frontend Dev, Backend Dev,
DevOps/QA) collaborate via CrewAI to design, write, and Docker-sandbox-test a
full-stack app from a single natural-language prompt — entirely offline.

## Prerequisites

1. **Docker** installed and running (Docker Desktop or a local `dockerd`).
2. **Ollama** installed and running:
   ```bash
   ollama serve
   ollama pull llama3.1:8b
   ollama pull codeqwen:7b
   ollama pull mistral:7b
   ```
   (Swap models in `llm_config.py` / via env vars for whatever you have pulled.)
3. Python 3.10+.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py "Build a full-stack to-do app with a React frontend and FastAPI backend"
```

Generated code lands in `./output/{frontend,backend}` with a QA report at
`./output/qa_report.md`. If QA reports a failure, one automatic corrective
fix-pass is triggered per component (configurable via `--max-fix-passes`).

## Configuration

All model/endpoint config lives in `llm_config.py` and reads from environment
variables, e.g.:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export BACKEND_MODEL=ollama/codeqwen:7b
```

No proprietary API keys are used or read anywhere in this codebase — the
config raises an error if a `gpt-*` or `claude-*` model string is ever set,
to guarantee the system stays fully local/offline.

## Sandbox safety notes

- Generated code runs only inside ephemeral Docker containers created by
  `sandbox_manager.py`, never on the host.
- Containers are network-isolated by default (`network_disabled=True`),
  memory/CPU-capped, and force-removed after every run.
- Enable network access only if your generated app needs it (e.g. `pip install`
  from PyPI): `SandboxManager(network_enabled=True)`.
