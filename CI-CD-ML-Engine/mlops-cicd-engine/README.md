# ML-Ops CI/CD Engine

Automated Git-triggered training pipeline: push a commit that touches `data/`
or `src/models/`, and the engine trains/fine-tunes a model, evaluates it
(precision-focused), checkpoints it if it beat the previous best, and shows
all of it on a live dashboard.

```
backend/    FastAPI app, webhook listener, ML pipeline
frontend/   React + TypeScript + Tailwind dashboard
```

## Run the backend

Requires Python 3.10+. The ML libraries (torch, transformers) are heavy —
install them where you actually have compute (GPU box, server). The API and
dashboard work without them too; only the pipeline's `torch`/`transformers`
imports need the full install.

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first launch it creates `mlops.db` (SQLite) and seeds a few demo runs so
the dashboard isn't empty. Swap `DATABASE_URL` (env var) for a Postgres DSN
in production — no code changes needed elsewhere.

API docs: http://localhost:8000/docs

## Run the frontend

Requires Node 18+.

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:5173

## Trigger a pipeline run

Send the mock Git payload to the webhook endpoint:

```bash
curl -X POST http://localhost:8000/api/webhooks/git \
  -H "Content-Type: application/json" \
  -d @backend/mock_data/sample_git_payload.json
```

Because the payload's commit touches `data/transactions_q3.csv`, it matches
a watched path and queues a run — watch it move from Queued → Running →
Success on the dashboard.

For a real repo, point GitHub/GitLab's push webhook at
`POST /api/webhooks/git` on your deployed backend.

## Repo-side config

Drop a `config.yaml` at the root of the watched repo (see
`backend/mock_data/config.yaml` for the full reference) to control which
model gets trained and how:

```yaml
model:
  source: local              # local | huggingface
  architecture: CustomCNN
  hf_model_id: distilbert-base-uncased

training:
  epochs: 5
  batch_size: 32
  learning_rate: 0.001
  val_split: 0.2

evaluation:
  precision_threshold: 0.85
```

## Notes on the ML wiring

- `app/ml/model_manager.py` — resolves `config.yaml` into either a local
  PyTorch architecture or a Hugging Face pretrained model + tokenizer.
- `app/ml/training.py` / `evaluation.py` — training loop and precision/
  recall/F1 evaluation. Ship with a minimal tabular demo so the pipeline is
  runnable out of the box; swap in your real data loaders and forward pass
  for production use (the shapes are intentionally left as clear extension
  points, commented in the code).
- `app/ml/pipeline_orchestrator.py` — coordinates a full run end-to-end and
  only checkpoints a model when its precision beats the current best *and*
  clears the `precision_threshold`.
- `backend/mock_data/` — a sample webhook payload, `config.yaml`, and a
  synthetic dataset so you can see the whole loop fire without a real repo.
