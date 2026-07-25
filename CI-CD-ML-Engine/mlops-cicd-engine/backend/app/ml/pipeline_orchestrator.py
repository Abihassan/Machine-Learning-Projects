"""
PipelineOrchestrator: coordinates one full pipeline run.

load config -> load model (local/HF) -> load+split data -> train ->
evaluate -> checkpoint if precision improved -> persist run + metrics.
"""
import time
import traceback
from datetime import datetime

from sqlalchemy.orm import Session

from app import config as app_config
from app.ml.model_manager import ModelManager
from app.ml import training, evaluation
from app.models import PipelineRun, ModelMetric, RegisteredModel, RunStatus, ModelSource


class PipelineOrchestrator:
    def __init__(self, db: Session, run: PipelineRun):
        self.db = db
        self.run = run

    def execute(self):
        self.run.status = RunStatus.RUNNING
        self.db.commit()
        start = time.time()

        try:
            cfg = app_config.load_repo_config()
            manager = ModelManager(cfg)
            loaded = manager.load()

            df = training.load_dataset()
            train_df, val_df = training.train_test_split_df(
                df, val_split=cfg["training"].get("val_split", 0.2)
            )

            is_hf = manager.source == "huggingface"
            if is_hf:
                trained = training.finetune_hf_model(loaded, train_df, cfg["training"])
                metrics = evaluation.evaluate_hf_model(loaded, val_df)
            else:
                trained = training.train_local_model(loaded, train_df, cfg["training"])
                metrics = evaluation.evaluate_local_model(trained, val_df)

            threshold = cfg["evaluation"].get("precision_threshold", 0.85)
            baseline = self._current_best_precision(is_hf)
            beat_baseline = metrics["precision"] > baseline and metrics["precision"] >= threshold

            metric_row = ModelMetric(
                run_id=self.run.id,
                precision=metrics["precision"],
                recall=metrics["recall"],
                f1_score=metrics["f1_score"],
                baseline_precision=baseline,
                beat_baseline=beat_baseline,
                epoch_count=cfg["training"].get("epochs", 0),
            )
            self.db.add(metric_row)

            if beat_baseline:
                self._checkpoint_and_register(cfg, manager, metrics["precision"], is_hf)

            self.run.status = RunStatus.SUCCESS

        except Exception as exc:  # noqa: BLE001 — surface any failure to the dashboard
            self.run.status = RunStatus.FAILED
            self.run.error_message = f"{exc}\n{traceback.format_exc(limit=3)}"

        finally:
            self.run.finished_at = datetime.utcnow()
            self.run.duration_seconds = time.time() - start
            self.db.commit()

    def _current_best_precision(self, is_hf: bool) -> float:
        source = ModelSource.HUGGINGFACE if is_hf else ModelSource.LOCAL
        best = (
            self.db.query(RegisteredModel)
            .filter(RegisteredModel.source == source)
            .order_by(RegisteredModel.top_precision.desc())
            .first()
        )
        return best.top_precision if best else 0.0

    def _checkpoint_and_register(self, cfg: dict, manager: ModelManager, precision: float, is_hf: bool):
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        checkpoint_name = f"{self.run.commit_hash[:8]}_{timestamp}.pt"
        checkpoint_path = app_config.CHECKPOINT_DIR / checkpoint_name

        # Deactivate previous active model of the same source
        source = ModelSource.HUGGINGFACE if is_hf else ModelSource.LOCAL
        self.db.query(RegisteredModel).filter(
            RegisteredModel.source == source, RegisteredModel.is_active.is_(True)
        ).update({"is_active": False})

        arch_or_id = (
            cfg["model"].get("hf_model_id") if is_hf else cfg["model"].get("architecture")
        )

        self.db.add(RegisteredModel(
            name=f"{arch_or_id}-{self.run.commit_hash[:8]}",
            source=source,
            architecture_or_hf_id=arch_or_id,
            version=timestamp,
            commit_hash=self.run.commit_hash,
            checkpoint_path=str(checkpoint_path),
            top_precision=precision,
            is_active=True,
        ))
        # NOTE: actual `torch.save(...)` write happens in a real training run;
        # omitted here to keep the demo runnable without a real dataset/model.
