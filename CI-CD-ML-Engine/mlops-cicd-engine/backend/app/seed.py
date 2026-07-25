"""Seeds a handful of demo pipeline runs + registered models so the
dashboard isn't empty on first launch. Only runs if the DB is empty."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import PipelineRun, ModelMetric, RegisteredModel, RunStatus, ModelSource


def seed_demo_data(db: Session):
    if db.query(PipelineRun).first():
        return  # already seeded

    now = datetime.utcnow()
    demo_runs = [
        dict(repo="acme/fraud-detector", branch="main", commit_hash="a1b2c3d4e5f6",
             commit_message="Add new transaction features", triggered_path="data/",
             status=RunStatus.SUCCESS, precision=0.91, recall=0.87, f1=0.89, beat=True),
        dict(repo="acme/fraud-detector", branch="main", commit_hash="9f8e7d6c5b4a",
             commit_message="Tune CNN kernel size", triggered_path="src/models/",
             status=RunStatus.SUCCESS, precision=0.88, recall=0.84, f1=0.86, beat=False),
        dict(repo="acme/fraud-detector", branch="feature/hf-swap", commit_hash="112233445566",
             commit_message="Swap to distilbert baseline", triggered_path="src/models/",
             status=RunStatus.FAILED, precision=None, recall=None, f1=None, beat=False),
        dict(repo="acme/fraud-detector", branch="main", commit_hash="deadbeef0001",
             commit_message="Refresh training set", triggered_path="data/",
             status=RunStatus.RUNNING, precision=None, recall=None, f1=None, beat=False),
    ]

    for i, d in enumerate(demo_runs):
        started = now - timedelta(hours=len(demo_runs) - i)
        finished = None if d["status"] == RunStatus.RUNNING else started + timedelta(minutes=6, seconds=i * 20)
        run = PipelineRun(
            repo=d["repo"], branch=d["branch"], commit_hash=d["commit_hash"],
            commit_message=d["commit_message"], triggered_path=d["triggered_path"],
            status=d["status"], started_at=started, finished_at=finished,
            duration_seconds=(finished - started).total_seconds() if finished else None,
            error_message="ValueError: tokenizer vocab mismatch with checkpoint" if d["status"] == RunStatus.FAILED else None,
        )
        db.add(run)
        db.flush()

        if d["precision"] is not None:
            db.add(ModelMetric(
                run_id=run.id, precision=d["precision"], recall=d["recall"],
                f1_score=d["f1"], baseline_precision=0.85, beat_baseline=d["beat"],
                epoch_count=5,
            ))

    db.add(RegisteredModel(
        name="CustomCNN-a1b2c3d4", source=ModelSource.LOCAL,
        architecture_or_hf_id="CustomCNN", version="20260722-081500",
        commit_hash="a1b2c3d4e5f6", checkpoint_path="./checkpoints/a1b2c3d4_20260722-081500.pt",
        top_precision=0.91, is_active=True,
    ))
    db.add(RegisteredModel(
        name="distilbert-base-uncased-9f8e7d6c", source=ModelSource.HUGGINGFACE,
        architecture_or_hf_id="distilbert-base-uncased", version="20260718-140210",
        commit_hash="9f8e7d6c5b4a", checkpoint_path="./checkpoints/9f8e7d6c_20260718-140210.pt",
        top_precision=0.83, is_active=False,
    ))

    db.commit()
