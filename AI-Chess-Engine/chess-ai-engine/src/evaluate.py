"""
evaluate.py
-----------
Plays `num_games` between two models (candidate vs. current best),
alternating colors each game to cancel out first-move advantage, using
low-temperature (near-greedy) MCTS move selection for both sides since
this is an evaluation match, not data generation.

Returns the candidate's win rate, counting draws as half a win each
(standard chess tournament scoring), which `train.py` compares against
the 55% promotion threshold.
"""

from __future__ import annotations
import torch
import chess

from mcts import MCTS


def play_evaluation_game(model_a, model_b, device: str = "cpu", num_simulations: int = 100,
                          max_moves: int = 200) -> str:
    """
    model_a plays White, model_b plays Black.
    Returns "1-0", "0-1", or "1/2-1/2".
    """
    model_a.eval()
    model_b.eval()
    mcts_a = MCTS(model_a, device=device, num_simulations=num_simulations)
    mcts_b = MCTS(model_b, device=device, num_simulations=num_simulations)

    board = chess.Board()
    ply = 0
    while not board.is_game_over(claim_draw=True) and ply < max_moves:
        mcts = mcts_a if board.turn == chess.WHITE else mcts_b
        # low temperature: near-greedy play for a fair strength comparison
        move, _, _ = mcts.select_move(board, temperature=0.1, add_root_noise=False)
        board.push(move)
        ply += 1

    if board.is_game_over(claim_draw=True):
        return board.result(claim_draw=True)
    return "1/2-1/2"  # move-limit reached, treat as draw


def evaluate_models(candidate, best_model, num_games: int = 20, num_simulations: int = 100,
                     device: str = "cpu", verbose: bool = True) -> float:
    """
    Plays `num_games` total, alternating which model has White each game.
    Returns candidate's win rate in [0, 1] (draws count as 0.5).
    """
    candidate_points = 0.0

    for game_idx in range(num_games):
        candidate_is_white = game_idx % 2 == 0
        if candidate_is_white:
            result = play_evaluation_game(candidate, best_model, device=device,
                                           num_simulations=num_simulations)
        else:
            result = play_evaluation_game(best_model, candidate, device=device,
                                           num_simulations=num_simulations)

        if result == "1/2-1/2":
            candidate_points += 0.5
        elif (result == "1-0" and candidate_is_white) or (result == "0-1" and not candidate_is_white):
            candidate_points += 1.0
        # else candidate lost, +0

        if verbose:
            print(f"  [eval] game {game_idx + 1}/{num_games}: result={result}, "
                  f"candidate was {'White' if candidate_is_white else 'Black'}")

    return candidate_points / num_games


if __name__ == "__main__":
    from model import ChessNet, ChessNetConfig

    cfg = ChessNetConfig(channels=16, num_blocks=1)
    model_a = ChessNet(cfg)
    model_b = ChessNet(cfg)

    win_rate = evaluate_models(model_a, model_b, num_games=2, num_simulations=10)
    print(f"\nCandidate win rate: {win_rate:.1%}")
