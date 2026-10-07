Absolutely — here is a **complete, polished GitHub-ready README** specifically for your Chess AI Engine. It is designed to look like a serious software/ML project rather than a basic documentation file.

:::writing{variant="document" id="74163" title="README.md"} \<div align="center"\>

# ♟️ Chess AI Engine

### AlphaZero-Style Self-Play Reinforcement Learning

**A full-stack chess AI combining PyTorch, neural-network evaluation, PUCT Monte Carlo Tree Search, self-play reinforcement learning, FastAPI, and a React/TypeScript interface.**

\<br/\>

!Python !PyTorch !FastAPI !React !TypeScript !Vite

\<br/\>

**🚀 Quick Start** · **🧠 Architecture** · **🎯 Training** · **🔌 API** · **🖥️ Frontend** · **🗺️ Roadmap**

\</div\>

---

## 🎮 What Is This?

This project is an end-to-end implementation of an **AlphaZero-style chess learning system**.

Instead of relying on a traditional hand-written chess evaluation function, the engine learns to evaluate positions and select moves using a combination of:

- 🧠 Deep residual neural networks
- 🌳 PUCT Monte Carlo Tree Search
- ♟️ Neural-network-guided self-play
- 🔁 Experience replay
- 📈 Candidate-vs-best model evaluation
- ⚡ GPU-accelerated training when available
- 🌐 FastAPI inference
- 🖥️ React/TypeScript chess interface

The result is a complete pipeline from **self-play → learning → evaluation → model promotion → API inference → interactive gameplay**.

> **This is an engineering-focused AlphaZero-style implementation designed to be runnable, testable, and extensible.**

---

# ✨ Features

\<table\> \<tr\> \<td width="33%" valign="top"\>

### 🧠 Neural Chess Model

- Residual CNN architecture
- Policy + value heads
- \~24.8M parameters
- 4,672-way policy output
- CUDA support

\</td\>

\<td width="33%" valign="top"\>

### 🌳 Monte Carlo Tree Search

- PUCT selection
- Neural policy priors
- Position value evaluation
- Tree expansion
- Backpropagation
- Configurable simulations

\</td\>

\<td width="33%" valign="top"\>

### ♟️ Self-Play RL

- Automated game generation
- MCTS-improved policies
- Position/outcome collection
- Replay buffer
- Iterative model improvement

\</td\> \</tr\>

\<tr\> \<td width="33%" valign="top"\>

### 🏆 Model Evaluation

- Candidate vs best model
- Alternating colors
- Draws count as ½ point
- \>55% promotion threshold
- Automatic checkpoint management

\</td\>

\<td width="33%" valign="top"\>

### ⚡ FastAPI Backend

- REST API
- FEN-based inference
- UCI + SAN moves
- Position evaluation
- Health endpoint
- Configurable MCTS

\</td\>

\<td width="33%" valign="top"\>

### 🖥️ Modern Web UI

- React + TypeScript
- Interactive chessboard
- Human vs AI
- Move history
- Evaluation display
- Backend status

\</td\> \</tr\> \</table\>

---

# 🏗️ Architecture

The project consists of three major layers:

```
flowchart TB

    subgraph ML["🧠 Machine Learning Engine"]
        BOARD["Chess Position"]
        ENCODE["Board Encoding"]
        MODEL["Residual CNN"]
        MCTS["PUCT MCTS"]
        SELFPLAY["Self-Play"]
        BUFFER["Replay Buffer"]
        TRAIN["Training"]
        EVAL["Candidate Evaluation"]
        CHECKPOINT["Best Model"]

        BOARD --> ENCODE
        ENCODE --> MODEL
        MODEL --> MCTS
        MCTS --> SELFPLAY
        SELFPLAY --> BUFFER
        BUFFER --> TRAIN
        TRAIN --> EVAL
        EVAL --> CHECKPOINT
        CHECKPOINT --> SELFPLAY
    end

    subgraph API["⚡ Backend"]
        FASTAPI["FastAPI"]
        INFERENCE["MCTS Inference"]
    end

    subgraph UI["🖥️ Frontend"]
        REACT["React + TypeScript"]
        BOARDUI["Interactive Chessboard"]
    end

    CHECKPOINT --> FASTAPI
    FASTAPI --> INFERENCE
    REACT --> BOARDUI
    BOARDUI --> FASTAPI
    INFERENCE --> BOARDUI
```

---

# 🧠 How the AI Works

The engine follows the fundamental AlphaZero-style loop:

```
                    ┌──────────────────────┐
                    │     Neural Model     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Self-Play       │
                    │    + MCTS Search     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Training Data     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Replay Buffer     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Train Candidate     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Candidate vs Best    │
                    └──────────┬───────────┘
                               │
                        Win Rate > 55%?
                          /          \
                        YES           NO
                         │             │
                         ▼             ▼
                   Promote Model    Discard
                         │
                         └───────────────► Self-Play
```

This allows the model to improve iteratively without requiring a manually written evaluation function.

---

# 🌳 Monte Carlo Tree Search

For every position, MCTS searches possible continuations before selecting a move.

```
flowchart LR

    P["Current Position"]
    N["Neural Network"]
    POLICY["Policy Priors"]
    VALUE["Position Value"]
    SELECT["PUCT Selection"]
    EXPAND["Expand Node"]
    EVAL["Evaluate"]
    BACK["Backpropagate"]
    MOVE["Select Move"]

    P --> N
    N --> POLICY
    N --> VALUE

    POLICY --> SELECT
    SELECT --> EXPAND
    EXPAND --> EVAL
    VALUE --> EVAL
    EVAL --> BACK
    BACK --> SELECT
    SELECT --> MOVE
```

The neural network provides two critical signals:

### Policy

A probability distribution over the **4,672 possible policy outputs**:

```
8 × 8 × 73 = 4,672
```

### Value

An estimate of the expected outcome of the current position.

MCTS combines these predictions with search statistics to choose the final move.

---

# 🧬 Neural Network

The model uses a residual convolutional backbone with separate policy and value heads.

```
                Chess Board
                     │
                     ▼
             19-Plane Encoding
                     │
                     ▼
           ┌───────────────────┐
           │   CNN Backbone    │
           │                   │
           │  Residual Block   │
           │  Residual Block   │
           │  Residual Block   │
           │       ...         │
           │  Residual Block   │
           └─────────┬─────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
        Policy Head      Value Head
              │             │
              ▼             ▼
         4,672 Moves     Position Value
```

### Default configuration

| Component | Configuration |
| --- | --- |
| Architecture | Residual CNN |
| Channels | 128 |
| Residual blocks | 10 |
| Parameters | \~24.8M |
| Policy outputs | 4,672 |
| Value output | Scalar |
| GPU | CUDA automatically used when available |

---

# ♟️ Board Representation

The current engine uses a **19-plane single-frame representation**.

This is intentionally smaller than the original AlphaZero 8-frame / 119-plane representation.

The trade-off is simple:

```
Full AlphaZero representation
        ↓
Higher information
        ↓
Higher compute + memory requirements

This project
        ↓
19-plane representation
        ↓
More accessible experimentation
```

The encoding layer is structured so historical board information can be introduced later.

---

# 🔄 Self-Play

Self-play is the engine's primary source of training data.

For every game:

```
Current Model
     │
     ▼
MCTS
     │
     ▼
Select Move
     │
     ▼
Play Move
     │
     ▼
Repeat until Game Ends
     │
     ▼
Game Outcome
```

Training examples contain the information needed to teach the network:

- Current board position
- MCTS-improved policy
- Final game outcome

These examples are stored in the replay buffer and sampled during training.

---

# 🏆 Model Promotion

A newly trained model does **not** automatically replace the existing model.

Instead:

```
             Candidate Model
                    │
                    ▼
             Play Evaluation
                    │
                    ▼
          ┌────────────────────┐
          │   Candidate vs     │
          │    Best Model      │
          └─────────┬──────────┘
                    │
                    ▼
              Win Rate > 55%?
                 /       \
               YES        NO
                │          │
                ▼          ▼
             Promote     Reject
                │
                ▼
       best_model.pt
```

Evaluation characteristics:

- Candidate plays against the current best model.
- Colors alternate.
- Draws count as half a point.
- Candidate must achieve **more than 55%** to replace the best model.

This creates a basic model-selection mechanism rather than blindly overwriting checkpoints.

---

# 📁 Project Structure

```
chess-ai-engine/
│
├── 📄 requirements.txt
│
├── 🧠 src/
│   ├── encoding.py
│   ├── model.py
│   ├── mcts.py
│   ├── self_play.py
│   ├── replay_buffer.py
│   ├── train.py
│   ├── evaluate.py
│   ├── test_phase1_2.py
│   └── test_phase3.py
│
├── ⚡ backend/
│   └── main.py
│
├── 🖥️ frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── apiClient.ts
│   │   └── main.tsx
│   └── ...
│
├── 💾 checkpoints/
│   └── best_model.pt
│
└── 📦 data/
    └── replay buffers
```

---

# 🚀 Quick Start

## 1\. Clone the project

```
git clone <repository-url>
cd chess-ai-engine
```

## 2\. Create Python environment

```
python3 -m venv venv
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate
```

## 3\. Install dependencies

```
pip install -r requirements.txt
```

---

# 🧪 Run Tests

Validate the core engine:

```
cd src

python3 test_phase1_2.py
python3 test_phase3.py
```

The tests cover the core encoding/model components and MCTS behavior.

The implementation has also been exercised with:

- Real MCTS searches
- Real self-play games
- Real training steps
- Real FastAPI requests
- Real frontend builds

---

# 🎯 Train the Engine

For a smoke test:

```
cd src
python3 train.py
```

For a larger training run:

```
from train import training_iteration_loop, TrainConfig

training_iteration_loop(
    num_iterations=50,
    games_per_iteration=25,
    num_simulations=200,
    train_config=TrainConfig(
        batch_size=256
    ),
)
```

### Training parameters

| Parameter | Purpose |
| --- | --- |
| `num_iterations` | Number of training cycles |
| `games_per_iteration` | Self-play games per cycle |
| `num_simulations` | MCTS simulations per move |
| `batch_size` | Neural-network training batch size |

---

# ⚡ Hardware & Performance

The default network contains approximately **24.8 million parameters**.

MCTS can become computationally expensive because each search requires repeated neural-network inference.

A rough relationship is:

```
More MCTS simulations
        ↓
More neural-network evaluations
        ↓
Stronger search
        ↓
Higher computation cost
```

For meaningful AlphaZero-style training, expect to need:

- CUDA-capable GPU
- Many self-play games
- Large replay buffers
- Many training iterations
- Significant compute time

The project is therefore best viewed as a **complete and extensible research/engineering pipeline**, rather than a claim of AlphaZero-level playing strength out of the box.

---

# 🔌 Backend API

Start the backend:

```
cd backend

pip install -r ../requirements.txt

uvicorn main:app --reload --port 8000
```

---

## Health Check

```
GET /health
```

Example:

```
{
  "status": "ok",
  "device": "cuda",
  "checkpoint_loaded": true
}
```

---

## Play a Move

```
POST /play
```

Request:

```
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}
```

The response provides information including:

```
Selected move
├── UCI notation
├── SAN notation
├── Value estimate
├── Check status
├── Checkmate status
├── Stalemate status
└── Resulting FEN
```

---

# ⚙️ Backend Configuration

The backend supports:

| Environment Variable | Default | Purpose |
| --- | --- | --- |
| `CHESS_CHECKPOINT_PATH` | `../checkpoints/best_model.pt` | Model checkpoint |
| `CHESS_NUM_SIMULATIONS` | `200` | MCTS simulations |

For faster local inference:

```
export CHESS_NUM_SIMULATIONS=50
```

The backend can also start without a checkpoint. In that situation it uses a randomly initialized model, which is useful for validating the complete application stack before training.

---

# 🖥️ Frontend

The frontend is built with:

- React
- TypeScript
- Vite
- `react-chessboard`

Start it with:

```
cd frontend

npm install
npm run dev
```

Then open:

```
http://localhost:5173
```

---

## 🎮 Current Gameplay

```
Human
  │
  │ Move piece
  ▼
React Chessboard
  │
  │ FEN
  ▼
FastAPI
  │
  ▼
MCTS + Neural Network
  │
  │ AI move
  ▼
React Chessboard
```

The interface currently supports:

- Human as White
- AI as Black
- Automatic AI responses
- Move history
- Position evaluation
- Backend connectivity status

---

## 🌐 Frontend Configuration

Create:

```
frontend/.env.local
```

Example:

```
VITE_API_BASE_URL=http://localhost:8000
```

Build the production frontend:

```
npm run build
```

---

# 🔬 Validation

The project has been validated across the complete stack.

| Layer | Validation |
| --- | --- |
| Board encoding | ✅ |
| Move encoding | ✅ |
| Promotions | ✅ |
| Castling | ✅ |
| En passant | ✅ |
| Neural model | ✅ |
| MCTS | ✅ |
| Self-play | ✅ |
| Training step | ✅ |
| Model evaluation | ✅ |
| FastAPI requests | ✅ |
| TypeScript compilation | ✅ |
| Vite production build | ✅ |

The objective is to ensure that the system is not merely a collection of theoretical components, but a functioning end-to-end pipeline.

---

# 🧩 Engineering Decisions

## Why 19 planes?

The full historical AlphaZero representation is expensive for experimentation.

The 19-plane representation provides a simpler starting point while keeping the model architecture extensible.

---

## Why rebuild the MCTS tree?

The current implementation rebuilds the search tree after every move.

This makes the search implementation simpler and easier to reason about.

A future version can reuse the subtree corresponding to the selected move.

---

## Why use candidate-vs-best evaluation?

Training loss alone does not guarantee stronger chess play.

A model can have a lower loss while performing worse against the previous model.

The evaluation stage introduces an actual gameplay-based promotion criterion.

---

# 🛣️ Roadmap

### Search

- [ ]MCTS tree reuse
- [ ]Parallel MCTS
- [ ]Virtual loss
- [ ]Improved exploration scheduling

### Training

- [ ]Distributed self-play
- [ ]Multi-GPU training
- [ ]Larger replay buffers
- [ ]Experiment tracking
- [ ]Training metrics dashboard

### Model

- [ ]Full historical board encoding
- [ ]Larger residual networks
- [ ]Improved initialization
- [ ]Supervised pretraining from PGN

### Backend

- [ ]WebSocket gameplay
- [ ]Streaming analysis
- [ ]API authentication
- [ ]Docker deployment

### Frontend

- [ ]Human color selection
- [ ]Board themes
- [ ]Evaluation bar
- [ ]Move annotations
- [ ]Engine analysis panel
- [ ]Game export/import
- [ ]PGN support

### Infrastructure

- [ ]Docker Compose
- [ ]Cloud deployment
- [ ]CI/CD
- [ ]Automated model evaluation
- [ ]Elo tracking

---

# 📊 Future Vision

The long-term architecture can evolve toward a distributed training system:

```
flowchart TB

    MASTER["🏆 Training Coordinator"]

    MASTER --> W1["Self-Play Worker 1"]
    MASTER --> W2["Self-Play Worker 2"]
    MASTER --> W3["Self-Play Worker 3"]
    MASTER --> WN["Self-Play Worker N"]

    W1 --> BUFFER["🔥 Distributed Replay Buffer"]
    W2 --> BUFFER
    W3 --> BUFFER
    WN --> BUFFER

    BUFFER --> GPU["🚀 GPU Training"]

    GPU --> CANDIDATE["Candidate Model"]

    CANDIDATE --> EVAL["⚔️ Evaluation Arena"]

    EVAL --> MASTER

    MASTER --> MODEL["Best Model"]
```

This would allow the current local implementation to evolve into a much larger-scale reinforcement-learning platform.

---

# 🧰 Technology Stack

| Area | Technology |
| --- | --- |
| Language | Python |
| Deep Learning | PyTorch |
| Chess Rules | python-chess |
| Search | PUCT MCTS |
| API | FastAPI |
| Server | Uvicorn |
| Frontend | React |
| Language | TypeScript |
| Build Tool | Vite |
| Chess UI | react-chessboard |
| Hardware Acceleration | CUDA |

---

# 💡 Project Goals

This project is designed around four principles:

### 01 — Correctness

The individual components should work together as an actual system.

### 02 — Reproducibility

A developer should be able to clone the repository, install dependencies, run tests, and execute the pipeline.

### 03 — Extensibility

The architecture should make it straightforward to replace or improve the model, search algorithm, training strategy, or frontend.

### 04 — Scale

The initial implementation should provide a foundation that can eventually grow from local experimentation into distributed self-play and GPU-heavy training.

---

# 🤝 Contributing

Contributions are welcome.

Potential areas for contribution include:

- MCTS optimizations
- Training performance
- Distributed self-play
- Model architecture improvements
- Frontend UX
- Evaluation tooling
- Deployment infrastructure
- Testing and benchmarking

A good contribution should include tests where appropriate and preserve the existing end-to-end workflow.

---

# 📄 License

Add the project's chosen license here.

For example:

```
MIT License
```

---

\<div align="center"\>

## ♟️ Built to Learn Chess. Engineered to Scale.

**Neural Networks × MCTS × Self-Play × Reinforcement Learning**

\<br/\>

⭐ Star the repository if you find the project interesting.

\</div\> :::
