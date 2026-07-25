"""
ModelManager: dynamic model loader.

Given the repo's config.yaml, instantiate either:
  - a local architecture defined in the repo (source: "local"), or
  - a pre-trained model pulled from Hugging Face (source: "huggingface").

Kept import-light at module load time (torch/transformers imported lazily
inside methods) so the rest of the API works even before the ML deps are
installed on a given machine.
"""
from typing import Any


class CustomCNN:
    """
    Placeholder local architecture. Replace with your real model class
    (or import it from the repo's src/models/ directory) — the manager
    just needs anything exposing forward()/predict() and state_dict().
    """

    def __init__(self, num_classes: int = 2):
        import torch.nn as nn

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.net = nn.Sequential(
                    nn.Conv2d(3, 16, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d(1),
                    nn.Flatten(),
                    nn.Linear(16, num_classes),
                )

            def forward(self, x):
                return self.net(x)

        self.module = _Net()


LOCAL_ARCHITECTURES = {
    "CustomCNN": CustomCNN,
}


class ModelManager:
    """Resolves a config.yaml `model` section into a loaded, ready-to-train model."""

    def __init__(self, config: dict):
        self.config = config.get("model", {})
        self.source = self.config.get("source", "local")

    def load(self) -> Any:
        if self.source == "local":
            return self._load_local()
        elif self.source == "huggingface":
            return self._load_huggingface()
        raise ValueError(f"Unknown model source: {self.source}")

    def _load_local(self) -> Any:
        arch_name = self.config.get("architecture", "CustomCNN")
        arch_cls = LOCAL_ARCHITECTURES.get(arch_name)
        if arch_cls is None:
            raise ValueError(
                f"Unknown local architecture '{arch_name}'. "
                f"Register it in LOCAL_ARCHITECTURES or add it to src/models/."
            )
        return arch_cls().module

    def _load_huggingface(self) -> Any:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        hf_id = self.config.get("hf_model_id", "distilbert-base-uncased")
        tokenizer = AutoTokenizer.from_pretrained(hf_id)
        model = AutoModelForSequenceClassification.from_pretrained(hf_id)
        return {"model": model, "tokenizer": tokenizer, "hf_id": hf_id}
