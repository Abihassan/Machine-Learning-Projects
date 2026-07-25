"""Global app settings + the repo-level config.yaml contract."""
import os
import yaml
from pathlib import Path

# Directories in the watched repo that trigger a pipeline run when touched.
WATCHED_PATHS = ["data/", "src/models/"]

# Where trained checkpoints get written.
CHECKPOINT_DIR = Path(os.getenv("CHECKPOINT_DIR", "./checkpoints"))
CHECKPOINT_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "model": {
        "source": "local",              # "local" | "huggingface"
        "architecture": "CustomCNN",     # used if source == local
        "hf_model_id": "distilbert-base-uncased",  # used if source == huggingface
    },
    "training": {
        "epochs": 5,
        "batch_size": 32,
        "learning_rate": 0.001,
        "val_split": 0.2,
    },
    "evaluation": {
        "precision_threshold": 0.85,
    },
}


def load_repo_config(config_path: str | Path = "config.yaml") -> dict:
    """
    Load the repo's config.yaml (hyperparameters + model source). Falls back
    to DEFAULT_CONFIG for any missing keys so a minimal repo config still works.
    """
    path = Path(config_path)
    if not path.exists():
        return DEFAULT_CONFIG

    with open(path) as f:
        user_config = yaml.safe_load(f) or {}

    merged = {**DEFAULT_CONFIG}
    for section, values in user_config.items():
        merged[section] = {**DEFAULT_CONFIG.get(section, {}), **values}
    return merged


def touches_watched_path(changed_files: list[str]) -> str | None:
    """Return the first watched path a commit's changed files touch, else None."""
    for changed in changed_files:
        for watched in WATCHED_PATHS:
            if changed.startswith(watched):
                return watched
    return None
