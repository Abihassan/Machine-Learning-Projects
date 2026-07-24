"""
train.py
--------
Trains ChessNet on batches sampled from a ReplayBuffer.

Loss (matches AlphaZero):
    L = (z - v)^2                         value: MSE
        - sum_a( pi_a * log(p_a) )        policy: cross-entropy against
                                           the MCTS visit-count distribution
        + c * ||theta||^2                 L2 regularization (via weight_decay)

Since policy targets `pi` are full soft distributions (not one-hot class
labels), we implement cross-entropy manually as
    -sum(pi * log_softmax(logits))
rather than using nn.CrossEntropyLoss (which expects a single target
class index).
"""

from __future__ import annotations
import os
import time
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from model import ChessNet, ChessNetConfig
from replay_buffer import ReplayBuffer, TrainingExample


class ReplayDataset(Dataset):
    def __init__(self, examples: list[TrainingExample]):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        return (
            torch.from_numpy(ex.state),
            torch.from_numpy(ex.policy),
            torch.tensor(ex.value, dtype=torch.float32),
        )


def policy_value_loss(policy_logits: torch.Tensor, value_pred: torch.Tensor,
                       policy_target: torch.Tensor, value_target: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Returns (total_loss, policy_loss, value_loss) -- all scalars."""
    log_probs = F.log_softmax(policy_logits, dim=1)
    policy_loss = -(policy_target * log_probs).sum(dim=1).mean()
    value_loss = F.mse_loss(value_pred.squeeze(-1), value_target)
    total = policy_loss + value_loss
    return total, policy_loss, value_loss


@dataclass
class TrainConfig:
    batch_size: int = 256
    epochs_per_iteration: int = 1
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    checkpoint_dir: str = "../checkpoints"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def train_on_buffer(model: ChessNet, buffer: ReplayBuffer, config: TrainConfig,
                     iteration: int) -> dict:
    """One training iteration: run `epochs_per_iteration` passes over the
    (shuffled) buffer contents, update weights, save a checkpoint.
    Returns a dict of average losses for logging."""
    model.to(config.device)
    model.train()

    dataset = ReplayDataset(list(buffer.buffer))
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True, drop_last=False)

    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate,
                                  weight_decay=config.weight_decay)

    total_losses, policy_losses, value_losses = [], [], []

    for epoch in range(config.epochs_per_iteration):
        for states, policies, values in loader:
            states = states.to(config.device)
            policies = policies.to(config.device)
            values = values.to(config.device)

            optimizer.zero_grad()
            policy_logits, value_pred = model(states)
            loss, p_loss, v_loss = policy_value_loss(policy_logits, value_pred, policies, values)
            loss.backward()
            optimizer.step()

            total_losses.append(loss.item())
            policy_losses.append(p_loss.item())
            value_losses.append(v_loss.item())

    os.makedirs(config.checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(config.checkpoint_dir, f"checkpoint_iter{iteration}.pt")
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": model.config,
        "iteration": iteration,
    }, checkpoint_path)

    metrics = {
        "iteration": iteration,
        "avg_total_loss": float(np.mean(total_losses)) if total_losses else 0.0,
        "avg_policy_loss": float(np.mean(policy_losses)) if policy_losses else 0.0,
        "avg_value_loss": float(np.mean(value_losses)) if value_losses else 0.0,
        "checkpoint_path": checkpoint_path,
    }
    return metrics


def training_iteration_loop(num_iterations: int, games_per_iteration: int,
                             num_simulations: int = 200, train_config: TrainConfig | None = None):
    """
    Full self-play -> train -> evaluate -> (maybe promote) cycle.
    This is the top-level orchestration script; run it directly, or import
    and call from a notebook/CLI wrapper.
    """
    from self_play import run_self_play
    from evaluate import evaluate_models

    config = train_config or TrainConfig()
    model_config = ChessNetConfig()

    best_model_path = os.path.join(config.checkpoint_dir, "best_model.pt")
    os.makedirs(config.checkpoint_dir, exist_ok=True)

    if os.path.exists(best_model_path):
        best_model = ChessNet(model_config)
        state = torch.load(best_model_path, map_location=config.device)
        best_model.load_state_dict(state["model_state_dict"])
        print(f"Resumed from {best_model_path}")
    else:
        best_model = ChessNet(model_config)
        torch.save({"model_state_dict": best_model.state_dict(), "config": model_config, "iteration": 0},
                    best_model_path)
        print("No existing best model -- starting from random init (cold start).")

    best_model.to(config.device)
    buffer = ReplayBuffer()

    for iteration in range(1, num_iterations + 1):
        print(f"\n=== Iteration {iteration}/{num_iterations} ===")

        print(f"[self-play] generating {games_per_iteration} games with current best model...")
        run_self_play(best_model, num_games=games_per_iteration, device=config.device,
                       num_simulations=num_simulations, buffer=buffer)

        print(f"[train] training candidate on {len(buffer)} buffered examples...")
        candidate = ChessNet(model_config)
        candidate.load_state_dict(best_model.state_dict())  # warm-start from current best
        metrics = train_on_buffer(candidate, buffer, config, iteration)
        print(f"[train] losses: total={metrics['avg_total_loss']:.4f} "
              f"policy={metrics['avg_policy_loss']:.4f} value={metrics['avg_value_loss']:.4f}")

        print("[evaluate] candidate vs best model...")
        win_rate = evaluate_models(candidate, best_model, num_games=20,
                                    num_simulations=max(50, num_simulations // 4), device=config.device)
        print(f"[evaluate] candidate win rate: {win_rate:.1%}")

        if win_rate > 0.55:
            print("[promote] candidate becomes new best model")
            best_model = candidate
            torch.save({"model_state_dict": best_model.state_dict(), "config": model_config,
                        "iteration": iteration}, best_model_path)
        else:
            print("[promote] candidate rejected, keeping current best model")


if __name__ == "__main__":
    # Small smoke-test run -- not a real training session, just proves the
    # wiring (self-play -> train -> evaluate -> promote/reject) works.
    training_iteration_loop(num_iterations=1, games_per_iteration=1, num_simulations=15,
                             train_config=TrainConfig(batch_size=32, checkpoint_dir="/tmp/chess_smoke_checkpoints"))
