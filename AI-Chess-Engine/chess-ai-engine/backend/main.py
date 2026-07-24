"""
backend/main.py
----------------
FastAPI app that loads the best local checkpoint and exposes a /play
endpoint: given a FEN string, runs a (short, inference-time) MCTS search
and returns the chosen move in UCI format.

Run with:
    cd backend
    uvicorn main:app --reload --port 8000

The model is loaded once at startup (module-level, via FastAPI's
lifespan hook) and reused across requests -- reloading a 25M-parameter
network per request would be far too slow.
"""

from __future__ import annotations
import os
import sys
from contextlib import asynccontextmanager

import torch
import chess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# allow importing sibling `src/` modules (encoding, model, mcts)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from model import ChessNet, ChessNetConfig  # noqa: E402
from mcts import MCTS  # noqa: E402

CHECKPOINT_PATH = os.environ.get(
    "CHESS_CHECKPOINT_PATH",
    os.path.join(os.path.dirname(__file__), "..", "checkpoints", "best_model.pt"),
)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
NUM_SIMULATIONS = int(os.environ.get("CHESS_NUM_SIMULATIONS", "200"))

# Populated at startup by the lifespan hook below.
state: dict = {"model": None, "mcts": None}


def load_model() -> ChessNet:
    config = ChessNetConfig()
    model = ChessNet(config)
    if os.path.exists(CHECKPOINT_PATH):
        checkpoint = torch.load(CHECKPOINT_PATH, map_location=DEVICE)
        model.load_state_dict(checkpoint["model_state_dict"])
        print(f"Loaded checkpoint: {CHECKPOINT_PATH}")
    else:
        print(f"WARNING: no checkpoint found at {CHECKPOINT_PATH}. "
              f"Serving a randomly-initialized (untrained) model -- "
              f"moves will be legal but not remotely strong. Run the "
              f"training pipeline (src/train.py) to produce a real checkpoint.")
    model.to(DEVICE)
    model.eval()
    return model


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = load_model()
    state["mcts"] = MCTS(state["model"], device=DEVICE, num_simulations=NUM_SIMULATIONS)
    yield
    state.clear()


app = FastAPI(title="Chess AI Engine", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite / CRA dev servers
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlayRequest(BaseModel):
    fen: str
    num_simulations: int | None = None  # optional per-request override

    @field_validator("fen")
    @classmethod
    def fen_must_be_valid(cls, v: str) -> str:
        try:
            chess.Board(v)
        except ValueError as e:
            raise ValueError(f"Invalid FEN: {e}")
        return v


class PlayResponse(BaseModel):
    move_uci: str
    move_san: str
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    is_game_over: bool
    value_estimate: float
    fen_after_move: str


class HealthResponse(BaseModel):
    status: str
    device: str
    checkpoint_loaded: bool


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        device=DEVICE,
        checkpoint_loaded=os.path.exists(CHECKPOINT_PATH),
    )


@app.post("/play", response_model=PlayResponse)
def play(request: PlayRequest) -> PlayResponse:
    board = chess.Board(request.fen)

    if board.is_game_over(claim_draw=True):
        raise HTTPException(status_code=400, detail="Game is already over for this position.")

    mcts = state["mcts"]
    if request.num_simulations is not None:
        mcts = MCTS(state["model"], device=DEVICE, num_simulations=request.num_simulations)

    try:
        move, _visit_probs, value = mcts.select_move(board, temperature=0.1, add_root_noise=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    san = board.san(move)
    board.push(move)

    return PlayResponse(
        move_uci=move.uci(),
        move_san=san,
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        is_stalemate=board.is_stalemate(),
        is_game_over=board.is_game_over(claim_draw=True),
        value_estimate=value,
        fen_after_move=board.fen(),
    )
