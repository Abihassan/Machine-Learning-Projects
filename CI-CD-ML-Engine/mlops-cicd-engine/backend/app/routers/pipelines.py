"""Pipeline run read endpoints — GET /api/pipelines, GET /api/pipelines/{id}"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import PipelineRun
from app.schemas import PipelineRunOut

router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])


@router.get("", response_model=list[PipelineRunOut])
def list_pipeline_runs(db: Session = Depends(get_db)):
    runs = (
        db.query(PipelineRun)
        .options(joinedload(PipelineRun.metrics))
        .order_by(PipelineRun.started_at.desc())
        .all()
    )
    return runs


@router.get("/{run_id}", response_model=PipelineRunOut)
def get_pipeline_run(run_id: str, db: Session = Depends(get_db)):
    run = (
        db.query(PipelineRun)
        .options(joinedload(PipelineRun.metrics))
        .filter(PipelineRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run
