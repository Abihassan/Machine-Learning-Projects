"""Model registry endpoints — GET /api/models"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RegisteredModel
from app.schemas import RegisteredModelOut

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=list[RegisteredModelOut])
def list_models(db: Session = Depends(get_db)):
    return (
        db.query(RegisteredModel)
        .order_by(RegisteredModel.top_precision.desc())
        .all()
    )
