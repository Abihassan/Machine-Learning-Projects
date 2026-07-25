"""Git webhook listener — POST /api/webhooks/git"""
from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import touches_watched_path
from app.models import PipelineRun, RunStatus
from app.ml.pipeline_orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _run_pipeline_task(run_id: str, db_factory):
    """Background task entrypoint — opens its own DB session."""
    db = db_factory()
    try:
        run = db.query(PipelineRun).get(run_id)
        if run:
            PipelineOrchestrator(db, run).execute()
    finally:
        db.close()


@router.post("/git")
async def receive_git_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    payload = await request.json()

    repo_name = payload.get("repository", {}).get("full_name", "unknown/unknown")
    ref = payload.get("ref", "refs/heads/main")
    branch = ref.split("/")[-1]

    head_commit = payload.get("head_commit") or {}
    commit_hash = head_commit.get("id")
    commit_message = head_commit.get("message", "")

    if not commit_hash:
        raise HTTPException(status_code=400, detail="Payload missing head_commit.id")

    changed_files = [
        *head_commit.get("added", []),
        *head_commit.get("modified", []),
        *head_commit.get("removed", []),
    ]
    watched_hit = touches_watched_path(changed_files)

    if not watched_hit:
        return {
            "triggered": False,
            "reason": "No changes under watched paths (data/, src/models/)",
        }

    run = PipelineRun(
        repo=repo_name,
        branch=branch,
        commit_hash=commit_hash,
        commit_message=commit_message,
        triggered_path=watched_hit,
        status=RunStatus.QUEUED,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    from app.database import SessionLocal
    background_tasks.add_task(_run_pipeline_task, run.id, SessionLocal)

    return {"triggered": True, "run_id": run.id}
