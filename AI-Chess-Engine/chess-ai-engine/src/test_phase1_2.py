"""
test_phase1_2.py
-----------------
Sanity checks for Phase 1 (env) and Phase 2 (model architecture):

1. Board encoding produces the right shape and sane values.
2. Move <-> index mapping is a bijection over all legal moves in a
   variety of positions (start position, midgame, endgame, promotions,
   castling, en passant).
3. The network runs a forward pass on a real encoded board and produces
   correctly-shaped policy/value outputs.
4. Legal-move masking + softmax gives a valid probability distribution
   restricted to legal moves only.

Run with: python3 test_phase1_2.py
"""

import sys
import torch
import torch.nn.functional as F
import chess
import chess.pgn
import io

from encoding import encode_board, move_to_index, legal_move_mask, INPUT_PLANES, POLICY_SIZE
from model import ChessNet, ChessNetConfig


def test_board_encoding():
    board = chess.Board()
    planes = encode_board(board)
    assert planes.shape == (INPUT_PLANES, 8, 8), f"bad shape {planes.shape}"
    # 16 white + 16 black pieces at start
    assert planes[0:6].sum() == 16, "white piece count wrong"
    assert planes[6:12].sum() == 16, "black piece count wrong"
    assert planes[12].sum() == 64, "white to move plane should be all 1s"
    print("[OK] test_board_encoding")


def test_move_index_bijection():
    """For a batch of diverse positions, every legal move must map to a
    unique index, and decoding via legal_move_mask must recover exactly
    the same move set."""
    test_fens = [
        chess.STARTING_FEN,
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",  # midgame
        "8/8/8/8/8/8/4k1P1/4K3 w - - 0 1",  # promotion-adjacent endgame
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",  # castling both sides
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3",  # en passant
        "8/P7/8/8/8/8/8/k6K w - - 0 1",  # promotion
    ]
    for fen in test_fens:
        board = chess.Board(fen)
        mask, index_to_move = legal_move_mask(board)
        legal = list(board.legal_moves)
        assert len(index_to_move) == len(legal), (
            f"collision or missing move for FEN {fen}: "
            f"{len(legal)} legal moves but {len(index_to_move)} unique indices"
        )
        # every legal move's UCI must appear among decoded moves
        decoded_ucis = {m.uci() for m in index_to_move.values()}
        legal_ucis = {m.uci() for m in legal}
        assert decoded_ucis == legal_ucis, f"mismatch for {fen}: {decoded_ucis ^ legal_ucis}"
    print(f"[OK] test_move_index_bijection ({len(test_fens)} positions)")


def test_model_forward_pass():
    cfg = ChessNetConfig(channels=32, num_blocks=2)  # small for a fast test
    net = ChessNet(cfg)
    net.eval()

    board = chess.Board()
    planes = encode_board(board)
    x = torch.from_numpy(planes).unsqueeze(0)  # (1, 19, 8, 8)

    policy_logits, value = net(x)
    assert policy_logits.shape == (1, POLICY_SIZE)
    assert value.shape == (1, 1)
    assert -1.0 <= value.item() <= 1.0
    print(f"[OK] test_model_forward_pass (value={value.item():.4f}, "
          f"policy_logits range=[{policy_logits.min().item():.3f}, {policy_logits.max().item():.3f}])")


def test_legal_move_masking_gives_valid_distribution():
    cfg = ChessNetConfig(channels=32, num_blocks=2)
    net = ChessNet(cfg)
    net.eval()

    board = chess.Board()
    planes = encode_board(board)
    x = torch.from_numpy(planes).unsqueeze(0)

    policy_logits, _ = net(x)
    mask, index_to_move = legal_move_mask(board)
    mask_t = torch.from_numpy(mask).unsqueeze(0)

    masked_logits = policy_logits.masked_fill(mask_t == 0, float("-inf"))
    probs = F.softmax(masked_logits, dim=1)

    assert torch.isclose(probs.sum(), torch.tensor(1.0), atol=1e-5)
    nonzero_indices = set((probs[0] > 1e-8).nonzero().flatten().tolist())
    assert nonzero_indices == set(index_to_move.keys())
    print(f"[OK] test_legal_move_masking_gives_valid_distribution "
          f"({len(index_to_move)} legal moves at start position)")


def test_full_game_replay_no_index_errors():
    """Play through a real short game and make sure every move at every
    ply encodes/decodes without error (catches perspective-flip bugs)."""
    pgn_text = """
1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5
7. Bb3 d6 8. c3 O-O 9. h3 Na5 10. Bc2 c5 11. d4 Qc7 1-0
"""
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    board = game.board()
    ply = 0
    for move in game.mainline_moves():
        assert move in board.legal_moves
        idx = move_to_index(move, board)
        mask, index_to_move = legal_move_mask(board)
        assert idx in index_to_move, f"ply {ply}: move {move.uci()} index {idx} not in legal mask"
        assert index_to_move[idx].uci() == move.uci()
        board.push(move)
        ply += 1
    print(f"[OK] test_full_game_replay_no_index_errors ({ply} plies)")


if __name__ == "__main__":
    tests = [
        test_board_encoding,
        test_move_index_bijection,
        test_model_forward_pass,
        test_legal_move_masking_gives_valid_distribution,
        test_full_game_replay_no_index_errors,
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
    print("\nAll Phase 1/2 sanity checks passed.")
