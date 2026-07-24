"""
FastAPI entrypoint.

Exposes:
  GET  /health           — is the API + Ollama + required models all ready?
  POST /api/models/pull   — trigger a pull for any configured model that's missing
  WS   /ws/agent          — send {"task": "..."}, receive a stream of AgentEvent
                             JSON objects as the LangGraph loop runs

Run with (from the backend/ directory):
    uvicorn app.main:app --reload --port 8000

See README.md for the full first-run checklist (Ollama, model pulls, the
sandbox image).
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import agent_graph
from app.agents.state import AgentState
from app.config import settings
from app.llm.ollama_admin import missing_models, ping_ollama, pull_model
from app.schemas import AgentRunRequest

app = FastAPI(title="AI Software Engineer Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUIRED_MODELS = [settings.planner_model, settings.coder_model, settings.reviewer_model]


@app.get("/health")
async def health():
    """
    Reports whether Ollama is reachable and whether the three configured
    models are actually pulled. The frontend polls this before enabling the
    chat input, so a first-time user sees "pull qwen2.5-coder first" instead
    of a confusing silent hang on their first prompt.
    """
    alive = await ping_ollama()
    missing = await missing_models(REQUIRED_MODELS) if alive else REQUIRED_MODELS
    return {
        "ollama_reachable": alive,
        "required_models": REQUIRED_MODELS,
        "missing_models": missing,
        "executor_backend": settings.executor_backend,
    }


@app.post("/api/models/pull")
async def pull_missing_models():
    """Pulls every configured model (planner/coder/reviewer) not yet present locally."""
    missing = await missing_models(REQUIRED_MODELS)
    for model in missing:
        await pull_model(model)
    return {"pulled": missing}


def _initial_state(payload: AgentRunRequest) -> AgentState:
    return {
        "task": payload.task,
        "max_iterations": payload.max_iterations or settings.max_debug_iterations,
        "plan": "",
        "dependencies": [],
        "code": "",
        "stdout": "",
        "stderr": "",
        "exit_code": 0,
        "success": False,
        "review_notes": "",
        "iteration": 0,
        "status": "running",
        "events": [],
    }


@app.websocket("/ws/agent")
async def agent_ws(websocket: WebSocket):
    """
    One connection can drive multiple runs sequentially — send another
    {"task": ...} after a run's "done" event to start the next one without
    reconnecting.
    """
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()

            try:
                payload = AgentRunRequest.model_validate_json(raw)
            except Exception as exc:
                await websocket.send_json(
                    {"type": "error", "agent": "system", "content": f"Bad request: {exc}", "iteration": 0}
                )
                continue

            try:
                # stream_mode="updates" yields only what each node just
                # returned (not the whole accumulated state); version="v2"
                # wraps that in LangGraph's current stable StreamPart
                # envelope: {"type": "updates", "ns": (...), "data": {...}}.
                async for chunk in agent_graph.astream(
                    _initial_state(payload), stream_mode="updates", version="v2"
                ):
                    if chunk["type"] != "updates":
                        continue
                    for _node_name, node_update in chunk["data"].items():
                        for event in (node_update or {}).get("events", []):
                            await websocket.send_json(event)
            except Exception as exc:
                await websocket.send_json(
                    {"type": "error", "agent": "system", "content": f"Agent run crashed: {exc}", "iteration": 0}
                )
                continue

            await websocket.send_json({"type": "done", "agent": "system", "content": "run complete", "iteration": 0})

    except WebSocketDisconnect:
        pass
