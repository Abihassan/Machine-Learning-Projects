"""Pydantic request/response schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ModelMetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    precision: float
    recall: float
    f1_score: float
    baseline_precision: Optional[float] = None
    beat_baseline: bool
    epoch_count: int


class PipelineRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    repo: str
    branch: str
    commit_hash: str
    commit_message: str
    triggered_path: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    metrics: list[ModelMetricOut] = []


class RegisteredModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source: str
    architecture_or_hf_id: str
    version: str
    commit_hash: Optional[str] = None
    top_precision: float
    is_active: bool
    created_at: datetime


# ---- Git webhook payload (subset of GitHub's push event we actually use) ----

class GitCommit(BaseModel):
    id: str
    message: str = ""
    added: list[str] = []
    modified: list[str] = []
    removed: list[str] = []


class GitPushPayload(BaseModel):
    ref: str  # e.g. "refs/heads/main"
    repository: dict
    head_commit: Optional[GitCommit] = None
    commits: list[GitCommit] = []
