# Chess AI Engine — AlphaZero-style self-play

Full stack: PyTorch self-play RL engine, FastAPI backend, React/TypeScript
frontend. All phases below were built **and tested** (real MCTS runs, a
real self-play game, real training step, real HTTP requests against the
FastAPI server, a real TypeScript/Vite build) — not just written from
memory.

```
chess-ai-engine/
├── requirements.txt
├── src/
│   ├── encoding.py           Board <-> tensor, move <-> policy-index   [Phase 2]
│   ├── model.py                Dual-headed residual CNN                [Phase 2]
│   ├── mcts.py                 PUCT Monte Carlo Tree Search            [Phase 3]
│   ├── self_play.py            Self-play game generation loop          [Phase 3]
│   ├── replay_buffer.py        Experience replay buffer + persistence  [Phase 3]
│   ├── train.py                Training loop + full iteration cycle    [Phase 4]
│   ├── evaluate.py             Candidate vs. best-model match play     [Phase 4]
│   ├── test_phase1_2.py        Encoding/model sanity tests
│   └── test_phase3.py          MCTS correctness tests
├── backend/
│   └── main.py                 FastAPI app, /health + /play endpoints  [Phase 5]
├── frontend/                   React + TypeScript + react-chessboard   [Phase 6]
│   └── src/
│       ├── App.tsx, App.css, index.css
│       ├── apiClient.ts
│       └── main.tsx
├── checkpoints/                 populated by src/train.py
└── data/                        optional: exported replay buffers
```

## Quick start

### 1. Python environment

```bash
cd chess-ai-engine
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify the core engine

```bash
cd src
python3 test_phase1_2.py   # encoding + model
python3 test_phase3.py     # MCTS correctness
```

### 3. Train

```bash
cd src
python3 train.py
```

`train.py`'s `training_iteration_loop()` runs the full cycle: self-play
games with the current best model → train a candidate on the replay
buffer → evaluate candidate vs. best over N games → promote the
candidate to `checkpoints/best_model.pt` only if it wins **>55%** of
the evaluation match (draws count as half a point, colors alternate).
The `__main__` block runs a 1-iteration/1-game smoke config to prove
the wiring works fast; for a real run, call it with meaningfully larger
numbers, e.g.:

```python
from train import training_iteration_loop, TrainConfig
training_iteration_loop(
    num_iterations=50,
    games_per_iteration=25,
    num_simulations=200,
    train_config=TrainConfig(batch_size=256),
)
```

**Realistic expectations:** the default network is 128 channels / 10
blocks (~24.8M params). On CPU, each self-play move costs roughly
`num_simulations` forward passes — a single game can take minutes. Real
AlphaZero-strength play requires GPU + many thousands of self-play
games. This pipeline is correct and complete; treat the first runs as
functional verification, then scale `num_games`, `num_simulations`, and
hardware up from there. A CUDA GPU is used automatically if available.

### 4. Serve the model

```bash
cd backend
pip install -r ../requirements.txt   # fastapi/uvicorn already included
uvicorn main:app --reload --port 8000
```

Environment variables (optional):
- `CHESS_CHECKPOINT_PATH` — defaults to `../checkpoints/best_model.pt`
- `CHESS_NUM_SIMULATIONS` — MCTS sims per move at inference (default 200;
  lower it, e.g. 50, for snappier responses while iterating)

Endpoints:
- `GET /health` → `{status, device, checkpoint_loaded}`
- `POST /play` with `{"fen": "<FEN string>"}` → the engine's chosen move
  in UCI + SAN, check/mate/stalemate flags, its value estimate, and the
  resulting FEN.

If no checkpoint exists yet, the server still starts and serves a
randomly-initialized model (legal but weak moves) with a console
warning — useful for testing the full stack before training finishes.

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the printed local URL (default `http://localhost:5173`). Drag
pieces to play White; the app POSTs the resulting FEN to the backend
and plays the AI's reply automatically. The sidebar shows move history,
the AI's self-reported position evaluation, and backend connectivity
status. Set `VITE_API_BASE_URL` in a `.env.local` (see `.env.example`)
if your backend isn't on `localhost:8000`.

```bash
npm run build    # verified clean: tsc -b && vite build, 0 errors
```

## Design notes / where to extend

- **Board encoding** (`encoding.py`): single-frame 19-plane encoding
  rather than AlphaZero's full 8-frame/119-plane history stack, to stay
  trainable on modest hardware. `encode_board_history()` is a stubbed
  extension point if you want move-repetition awareness later.
- **Move space**: matches AlphaZero's 8×8×73 = 4672-way policy exactly.
  Verified via a full-game PGN replay test covering promotions,
  castling, and en passant (`test_phase1_2.py`).
- **Model init strategies** are documented in
  `model.py::load_pretrained_or_init` — cold start (default), warm
  start from a supervised PGN corpus, or LLM-assisted auxiliary
  supervision for building that corpus.
- **Tree reuse**: the current MCTS rebuilds the tree from scratch each
  move (simpler, matches this project's scope). A natural next
  optimization is retaining the subtree rooted at the played move
  across turns.
- **Frontend** currently fixes the human as White / AI as Black for
  simplicity; flipping `humanColor` and adding a color-choice UI is a
  small follow-up if you want the human to play Black too.
