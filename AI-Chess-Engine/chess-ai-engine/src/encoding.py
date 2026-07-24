"""
encoding.py
-----------
Converts between python-chess objects and the tensor representations
used by the neural network.

Board encoding
==============
We encode a single position as an (INPUT_PLANES, 8, 8) float tensor:

    planes 0-5   : white piece occupancy (P, N, B, R, Q, K)
    planes 6-11  : black piece occupancy (p, n, b, r, q, k)
    plane  12    : side to move (all 1s if white to move, else all 0s)
    plane  13    : white kingside castling right
    plane  14    : white queenside castling right
    plane  15    : black kingside castling right
    plane  16    : black queenside castling right
    plane  17    : en-passant target square (one-hot, all zeros if none)
    plane  18    : halfmove clock / 100 (normalized no-progress counter)

This is a single-frame simplification of AlphaZero's 8-frame history
stack (which uses 119 planes). It's enough to learn strong play and is
far cheaper to train on a single machine. History stacking is noted as
a documented extension point (see `encode_board_history`).

Move encoding
=============
Policy head output has size 8*8*73 = 4672, matching AlphaZero:
  - For each of the 64 "from" squares, there are 73 possible move types:
      56  queen-like moves: 8 directions x 7 distances (1..7 squares)
      8   knight moves
      9   underpromotions: 3 forward directions x 3 promotion pieces
          (N, B, R) -- queen promotions are encoded as a queen-like move
          of distance 1 in the forward direction (matches AlphaZero).

We build the move <-> index maps once at import time.
"""

from __future__ import annotations
import chess
import numpy as np

INPUT_PLANES = 19
BOARD_SIZE = 8
POLICY_SIZE = 8 * 8 * 73  # 4672

PIECE_TO_PLANE = {
    (chess.PAWN, chess.WHITE): 0,
    (chess.KNIGHT, chess.WHITE): 1,
    (chess.BISHOP, chess.WHITE): 2,
    (chess.ROOK, chess.WHITE): 3,
    (chess.QUEEN, chess.WHITE): 4,
    (chess.KING, chess.WHITE): 5,
    (chess.PAWN, chess.BLACK): 6,
    (chess.KNIGHT, chess.BLACK): 7,
    (chess.BISHOP, chess.BLACK): 8,
    (chess.ROOK, chess.BLACK): 9,
    (chess.QUEEN, chess.BLACK): 10,
    (chess.KING, chess.BLACK): 11,
}

# ---------------------------------------------------------------------
# Board -> tensor
# ---------------------------------------------------------------------

def encode_board(board: chess.Board) -> np.ndarray:
    """Encode a chess.Board into an (INPUT_PLANES, 8, 8) float32 array."""
    planes = np.zeros((INPUT_PLANES, BOARD_SIZE, BOARD_SIZE), dtype=np.float32)

    for square, piece in board.piece_map().items():
        row = chess.square_rank(square)
        col = chess.square_file(square)
        plane_idx = PIECE_TO_PLANE[(piece.piece_type, piece.color)]
        planes[plane_idx, row, col] = 1.0

    if board.turn == chess.WHITE:
        planes[12, :, :] = 1.0

    planes[13, :, :] = 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0
    planes[14, :, :] = 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0
    planes[15, :, :] = 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0
    planes[16, :, :] = 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0

    if board.ep_square is not None:
        row = chess.square_rank(board.ep_square)
        col = chess.square_file(board.ep_square)
        planes[17, row, col] = 1.0

    planes[18, :, :] = min(board.halfmove_clock, 100) / 100.0

    return planes


def encode_board_history(boards: list[chess.Board], history_len: int = 8) -> np.ndarray:
    """
    Optional extension point: stack `history_len` most-recent positions
    (most recent last) the way full AlphaZero does, for models that want
    move-repetition / history awareness. Pads with zero-planes if fewer
    positions are available. Returns (history_len * INPUT_PLANES, 8, 8).

    Not used by the baseline model in this project, but the model
    architecture's input channel count can be swapped to
    `history_len * INPUT_PLANES` to opt into this.
    """
    recent = boards[-history_len:]
    pad = history_len - len(recent)
    frames = [np.zeros((INPUT_PLANES, BOARD_SIZE, BOARD_SIZE), dtype=np.float32)] * pad
    frames += [encode_board(b) for b in recent]
    return np.concatenate(frames, axis=0)


# ---------------------------------------------------------------------
# Move <-> policy index
# ---------------------------------------------------------------------

_DIRECTIONS = [
    (1, 0), (1, 1), (0, 1), (-1, 1),
    (-1, 0), (-1, -1), (0, -1), (1, -1),
]  # N, NE, E, SE, S, SW, W, NW  (file_delta, rank_delta) style below uses (df, dr)

_KNIGHT_DELTAS = [
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2),
]

_UNDERPROMO_PIECES = [chess.KNIGHT, chess.BISHOP, chess.ROOK]
_UNDERPROMO_DIRS = [(-1, 1), (0, 1), (1, 1)]  # relative to white's forward direction


def _plane_for_queen_move(df: int, dr: int, dist: int) -> int:
    direction_idx = _DIRECTIONS.index((df, dr))
    return direction_idx * 7 + (dist - 1)  # planes 0-55


def _plane_for_knight_move(df: int, dr: int) -> int:
    return 56 + _KNIGHT_DELTAS.index((df, dr))  # planes 56-63


def _plane_for_underpromo(df: int, promo_piece: int) -> int:
    dir_idx = _UNDERPROMO_DIRS.index((df, 1))
    piece_idx = _UNDERPROMO_PIECES.index(promo_piece)
    return 64 + dir_idx * 3 + piece_idx  # planes 64-72


def move_to_index(move: chess.Move, board: chess.Board) -> int:
    """
    Map a legal chess.Move to an index in [0, 4672).
    Moves are always encoded from the mover's own perspective (i.e. as if
    they were White moving "up the board"), so the same plane layout is
    reused for both colors -- this is what AlphaZero does, and it halves
    the effective symmetry the network needs to learn.
    """
    from_sq, to_sq = move.from_square, move.to_square
    from_file, from_rank = chess.square_file(from_sq), chess.square_rank(from_sq)
    to_file, to_rank = chess.square_file(to_sq), chess.square_rank(to_sq)

    df, dr = to_file - from_file, to_rank - from_rank
    if board.turn == chess.BLACK:
        # flip perspective so "forward" is always +rank
        df, dr = -df, -dr
        from_file, from_rank = 7 - from_file, 7 - from_rank

    if move.promotion and move.promotion != chess.QUEEN:
        plane = _plane_for_underpromo(df, move.promotion)
    elif abs(df) + abs(dr) == 3 and abs(df) in (1, 2) and abs(dr) in (1, 2):
        plane = _plane_for_knight_move(df, dr)
    else:
        dist = max(abs(df), abs(dr))
        unit_df = 0 if df == 0 else df // abs(df)
        unit_dr = 0 if dr == 0 else dr // abs(dr)
        plane = _plane_for_queen_move(unit_df, unit_dr, dist)

    from_sq_norm = from_rank * 8 + from_file
    return from_sq_norm * 73 + plane


def legal_move_mask(board: chess.Board) -> tuple[np.ndarray, dict[int, chess.Move]]:
    """
    Returns:
        mask: (4672,) float32 array, 1.0 for legal moves, 0.0 elsewhere
        index_to_move: dict mapping policy index -> chess.Move (UCI-ready)
    """
    mask = np.zeros(POLICY_SIZE, dtype=np.float32)
    index_to_move: dict[int, chess.Move] = {}
    for move in board.legal_moves:
        idx = move_to_index(move, board)
        mask[idx] = 1.0
        index_to_move[idx] = move
    return mask, index_to_move


def result_to_value(result: str, side_to_move_was_white: bool) -> float:
    """Convert a PGN-style result string to a scalar in [-1, 1] from the
    perspective of the player who was to move at that recorded state."""
    if result == "1/2-1/2":
        return 0.0
    white_won = result == "1-0"
    if side_to_move_was_white:
        return 1.0 if white_won else -1.0
    else:
        return -1.0 if white_won else 1.0
