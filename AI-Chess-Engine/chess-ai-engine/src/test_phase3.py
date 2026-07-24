"""
test_phase3.py
---------------
Correctness checks for MCTS + self-play + replay buffer that go beyond
"it runs" -- specifically the parts that are easy to get subtly wrong:
terminal-node value assignment, visit-count bookkeeping, and buffer
round-tripping through disk.
"""

import os
import sys
import numpy as np
import torch
import chess

from model import ChessNet, ChessNetConfig
from mcts import MCTS
from replay_buffer import ReplayBuffer, TrainingExample
from encoding import POLICY_SIZE


def small_model():
    return ChessNet(ChessNetConfig(channels=16, num_blocks=1))


def test_mcts_picks_legal_move():
    model = small_model()
    model.eval()
    mcts = MCTS(model, num_simulations=20)
    board = chess.Board()
    move, visit_probs, value = mcts.select_move(board, temperature=1.0, add_root_noise=True)
    assert move in board.legal_moves
    assert abs(sum(visit_probs.values()) - 1.0) < 1e-6
    assert -1.0 <= value <= 1.0
    print("[OK] test_mcts_picks_legal_move")


def test_mcts_detects_checkmate_terminal_value():
    """Fool's mate position: black to move is already checkmated.
    Root expansion must hit the terminal branch correctly for any child
    that leads to checkmate, and a position that IS checkmate must
    never be expanded further."""
    # Position after 1. f3 e5 2. g4 Qh4# (white is checkmated, white to move... 
    # actually after Qh4# it's white's turn and white has no legal moves)
    board = chess.Board()
    for uci in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        board.push(chess.Move.from_uci(uci))
    assert board.is_checkmate()

    model = small_model()
    model.eval()
    mcts = MCTS(model, num_simulations=1)
    root = mcts_root = MCTS(model, num_simulations=1)
    root_node, visit_probs = mcts_root.run(board)
    # terminal position: no legal moves, so no children should be created
    assert len(root_node.children) == 0
    assert visit_probs == {}
    print("[OK] test_mcts_detects_checkmate_terminal_value")


def test_mcts_root_visit_counts_sum_correctly():
    model = small_model()
    model.eval()
    num_sims = 30
    mcts = MCTS(model, num_simulations=num_sims)
    board = chess.Board()
    root, visit_probs = mcts.run(board)
    total_child_visits = sum(child.visit_count for child in root.children.values())
    # root itself is visited once per simulation (it's on every path),
    # each simulation also increments exactly one child subtree total by 1
    # at the immediate child level -> total child visits == num_simulations
    assert total_child_visits == num_sims, f"expected {num_sims}, got {total_child_visits}"
    print("[OK] test_mcts_root_visit_counts_sum_correctly")


def test_replay_buffer_roundtrip(tmp_path="/tmp/test_buffer.npz"):
    buf = ReplayBuffer()
    for _ in range(5):
        buf.add_game([TrainingExample(
            state=np.random.rand(19, 8, 8).astype(np.float32),
            policy=np.random.rand(POLICY_SIZE).astype(np.float32),
            value=float(np.random.choice([-1.0, 0.0, 1.0])),
        )])
    buf.save(tmp_path)

    buf2 = ReplayBuffer()
    buf2.load(tmp_path)
    assert len(buf2) == len(buf)
    np.testing.assert_allclose(buf.buffer[0].state, buf2.buffer[0].state)
    os.remove(tmp_path)
    print("[OK] test_replay_buffer_roundtrip")


if __name__ == "__main__":
    tests = [
        test_mcts_picks_legal_move,
        test_mcts_detects_checkmate_terminal_value,
        test_mcts_root_visit_counts_sum_correctly,
        test_replay_buffer_roundtrip,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {t.__name__}: {e}")
    if failed:
        print(f"\n{failed} test(s) failed.")
        sys.exit(1)
    print("\nAll Phase 3 sanity checks passed.")
