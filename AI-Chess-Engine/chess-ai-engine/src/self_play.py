"""
self_play.py
------------
Generates training data by having the current best model play against
itself, using MCTS-guided move selection at every ply.

Per-move procedure:
    1. Run MCTS (with Dirichlet noise at the root for exploration).
    2. Record (encoded_state, visit_prob_distribution) as a pending
       training example -- the value target isn't known yet.
    3. Sample a move from the visit distribution using a temperature
       schedule: higher temperature (more random) for the opening
       moves, then temperature -> 0 (best move) later in the game, as
       AlphaZero does (this balances opening diversity for data
       generation against endgame precision).
    4. Push the move, repeat until the game ends.

Once the game ends, every recorded example is assigned the game outcome
(+1 / -1 / 0) from the perspective of the player to move at that state,
via `result_to_value`.
"""

from __future__ import annotations
import time
import numpy as np
import torch
import chess

from encoding import encode_board, POLICY_SIZE
from mcts import MCTS
from replay_buffer import TrainingExample, ReplayBuffer


def temperature_for_ply(ply: int, temp_threshold: int = 15) -> float:
    """High temperature (diverse move sampling) for the first
    `temp_threshold` plies, then deterministic best-move play."""
    return 1.0 if ply < temp_threshold else 0.05


def play_one_game(model, device: str = "cpu", num_simulations: int = 200,
                   c_puct: float = 1.5, temp_threshold: int = 15,
                   max_moves: int = 200) -> list[TrainingExample]:
    """Play a single self-play game to completion and return the
    resulting training examples (states/policies fully filled in with
    the final game outcome as value target)."""
    model.eval()
    mcts = MCTS(model, device=device, c_puct=c_puct, num_simulations=num_simulations)

    board = chess.Board()
    pending: list[tuple[np.ndarray, np.ndarray, bool]] = []  # (state, policy, was_white_to_move)

    ply = 0
    while not board.is_game_over(claim_draw=True) and ply < max_moves:
        temperature = temperature_for_ply(ply, temp_threshold)
        move, visit_probs, _root_value = mcts.select_move(
            board, temperature=temperature, add_root_noise=True
        )

        policy_target = np.zeros(POLICY_SIZE, dtype=np.float32)
        for idx, prob in visit_probs.items():
            policy_target[idx] = prob

        state = encode_board(board)
        pending.append((state, policy_target, board.turn == chess.WHITE))

        board.push(move)
        ply += 1

    result = board.result(claim_draw=True) if board.is_game_over(claim_draw=True) else "1/2-1/2"

    examples: list[TrainingExample] = []
    for state, policy, was_white in pending:
        if result == "1/2-1/2":
            value = 0.0
        else:
            white_won = result == "1-0"
            value = (1.0 if white_won else -1.0) if was_white else (-1.0 if white_won else 1.0)
        examples.append(TrainingExample(state=state, policy=policy, value=value))

    return examples


def run_self_play(model, num_games: int, device: str = "cpu", num_simulations: int = 200,
                   buffer: ReplayBuffer | None = None, verbose: bool = True) -> ReplayBuffer:
    """Play `num_games` self-play games and add all resulting examples to
    (a new or provided) replay buffer."""
    if buffer is None:
        buffer = ReplayBuffer()

    for game_idx in range(num_games):
        start = time.time()
        examples = play_one_game(model, device=device, num_simulations=num_simulations)
        buffer.add_game(examples)
        if verbose:
            elapsed = time.time() - start
            print(f"[self-play] game {game_idx + 1}/{num_games}: "
                  f"{len(examples)} plies, {elapsed:.1f}s, buffer size={len(buffer)}")

    return buffer


if __name__ == "__main__":
    from model import ChessNet, ChessNetConfig

    # Small/fast config purely to demonstrate the loop runs end-to-end.
    cfg = ChessNetConfig(channels=32, num_blocks=2)
    model = ChessNet(cfg)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    buffer = run_self_play(model, num_games=1, device=device, num_simulations=25)
    print(f"\nGenerated {len(buffer)} training examples from self-play.")
    example = buffer.buffer[0]
    print(f"Example shapes: state={example.state.shape}, policy={example.policy.shape}, value={example.value}")
