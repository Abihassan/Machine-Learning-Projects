"""ORM models: PipelineRun, ModelMetric, RegisteredModel."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Enum, ForeignKey, Boolean, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


class RunStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class ModelSource(str, enum.Enum):
    LOCAL = "local"
    HUGGINGFACE = "huggingface"


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(String, primary_key=True, default=gen_id)
    repo = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    commit_hash = Column(String, nullable=False)
    commit_message = Column(String, default="")
    triggered_path = Column(String, default="")  # which watched path triggered this run
    status = Column(Enum(RunStatus), default=RunStatus.QUEUED, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    metrics = relationship("ModelMetric", back_populates="run", cascade="all, delete-orphan")


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(String, primary_key=True, default=gen_id)
    run_id = Column(String, ForeignKey("pipeline_runs.id"), nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    baseline_precision = Column(Float, nullable=True)
    beat_baseline = Column(Boolean, default=False)
    epoch_count = Column(Integer, default=0)

    run = relationship("PipelineRun", back_populates="metrics")


class RegisteredModel(Base):
    __tablename__ = "registered_models"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    source = Column(Enum(ModelSource), nullable=False)
    architecture_or_hf_id = Column(String, nullable=False)  # e.g. "CustomCNN" or "distilbert-base-uncased"
    version = Column(String, nullable=False)
    commit_hash = Column(String, nullable=True)
    checkpoint_path = Column(String, nullable=True)
    top_precision = Column(Float, default=0.0)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
