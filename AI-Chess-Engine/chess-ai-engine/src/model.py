"""
model.py
--------
Dual-headed residual CNN: given an encoded board position, outputs

    policy: (POLICY_SIZE,) logits over the 4672 possible moves
    value:  scalar in [-1, 1], predicted game outcome for the side to move

Architecture mirrors AlphaZero's network at reduced scale so it's
trainable on a single GPU/CPU:

    input (19, 8, 8)
      -> conv stem (3x3, C channels) + BN + ReLU
      -> N residual blocks (3x3 conv, BN, ReLU, 3x3 conv, BN, +skip, ReLU)
      -> policy head: 1x1 conv -> 73 channels -> flatten -> FC(4672)
      -> value head:  1x1 conv -> 1 channel   -> flatten -> FC(256) -> FC(1) -> tanh

Default config (`ChessNetConfig`) uses 10 residual blocks / 128 channels
(~5M params) -- enough to learn strong tactics quickly on modest hardware.
Bump `num_blocks`/`channels` up (AlphaZero used 19-40 blocks / 256
channels) once you have more compute.
"""

from __future__ import annotations
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

from encoding import INPUT_PLANES, POLICY_SIZE


@dataclass
class ChessNetConfig:
    input_planes: int = INPUT_PLANES
    channels: int = 128
    num_blocks: int = 10
    policy_size: int = POLICY_SIZE
    value_hidden: int = 256


class ResidualBlock(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return F.relu(out)


class ChessNet(nn.Module):
    def __init__(self, config: ChessNetConfig = ChessNetConfig()):
        super().__init__()
        self.config = config
        c = config.channels

        # Stem
        self.stem_conv = nn.Conv2d(config.input_planes, c, kernel_size=3, padding=1, bias=False)
        self.stem_bn = nn.BatchNorm2d(c)

        # Residual tower
        self.tower = nn.Sequential(*[ResidualBlock(c) for _ in range(config.num_blocks)])

        # Policy head
        self.policy_conv = nn.Conv2d(c, 73, kernel_size=1, bias=False)
        self.policy_bn = nn.BatchNorm2d(73)
        self.policy_fc = nn.Linear(73 * 8 * 8, config.policy_size)

        # Value head
        self.value_conv = nn.Conv2d(c, 1, kernel_size=1, bias=False)
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(8 * 8, config.value_hidden)
        self.value_fc2 = nn.Linear(config.value_hidden, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        x: (batch, input_planes, 8, 8)
        returns:
            policy_logits: (batch, policy_size)  -- raw logits, apply softmax
                            masked to legal moves at inference time
            value:         (batch, 1) in [-1, 1]
        """
        out = F.relu(self.stem_bn(self.stem_conv(x)))
        out = self.tower(out)

        p = F.relu(self.policy_bn(self.policy_conv(out)))
        p = p.view(p.size(0), -1)
        policy_logits = self.policy_fc(p)

        v = F.relu(self.value_bn(self.value_conv(out)))
        v = v.view(v.size(0), -1)
        v = F.relu(self.value_fc1(v))
        value = torch.tanh(self.value_fc2(v))

        return policy_logits, value

    @torch.no_grad()
    def predict(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Inference helper: returns policy probabilities (softmax) and value."""
        self.eval()
        policy_logits, value = self.forward(x)
        policy_probs = F.softmax(policy_logits, dim=1)
        return policy_probs, value

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def load_pretrained_or_init(checkpoint_path: str | None, config: ChessNetConfig = ChessNetConfig(),
                             device: str = "cpu") -> ChessNet:
    """
    Load a local checkpoint if it exists, otherwise initialize fresh weights.

    Notes on "pre-trained local model" initialization strategies:
    1. Cold start (default here): random init, learn purely from self-play.
       This is what original AlphaZero does and what this project defaults to.
    2. Warm start from supervised data: pre-train the same ChessNet on a
       database of human games (e.g. Lichess PGN dumps) using move
       played -> policy target (cross-entropy) and game result -> value
       target, BEFORE self-play. This gives self-play a much stronger
       starting point and is the recommended path if you have a PGN
       corpus available locally. Use `pretrain.py` (Phase 4 add-on) for
       this -- same architecture, different data source, then save a
       checkpoint here and treat it as iteration 0 of self-play.
    3. Distillation from a local LLM: if you want to leverage a local
       Ollama/HF model that "knows" chess concepts from text, you can't
       transplant weights directly (incompatible architectures), but you
       can use it to *generate* candidate opening lines / commentary as
       auxiliary supervised signal for approach #2. This is optional and
       not required for the core AlphaZero-style pipeline.

    This function only handles the mechanical part: load weights from
    `checkpoint_path` if given and present on disk, else return a fresh
    network with random init (PyTorch's default Kaiming/uniform init for
    Conv2d/Linear layers is used as-is, which works well for this depth).
    """
    model = ChessNet(config).to(device)
    if checkpoint_path is not None:
        import os
        if os.path.exists(checkpoint_path):
            state = torch.load(checkpoint_path, map_location=device)
            model.load_state_dict(state["model_state_dict"] if "model_state_dict" in state else state)
            print(f"Loaded checkpoint from {checkpoint_path}")
        else:
            print(f"No checkpoint found at {checkpoint_path}, initializing fresh weights.")
    return model


if __name__ == "__main__":
    cfg = ChessNetConfig()
    net = ChessNet(cfg)
    print(f"ChessNet initialized: {net.num_parameters():,} trainable parameters")
    dummy = torch.zeros((2, cfg.input_planes, 8, 8))
    policy_logits, value = net(dummy)
    print("policy_logits shape:", policy_logits.shape)
    print("value shape:", value.shape)
