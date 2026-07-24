"""
mcts.py
-------
PUCT (Predictor + Upper Confidence bound applied to Trees) search, as
used in AlphaZero. The tree is built fresh for each search call (no
persistence across moves in this baseline -- see `advance_root` for an
optional tree-reuse optimization).

Core loop, `num_simulations` times:
    1. SELECT: walk down the tree from the root, at each node picking
       the child that maximizes  Q(s,a) + U(s,a)  where
           U(s,a) = c_puct * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
       until reaching a leaf (unexpanded node).
    2. EXPAND: run the neural network on the leaf position to get a
       policy distribution over legal moves and a value estimate.
       Create child nodes for every legal move, priors = network policy
       (masked + renormalized to legal moves).
    3. BACKUP: propagate the leaf's value back up the path, flipping
       sign at each ply (since value is always from the perspective of
       the player to move at that node).

After all simulations, the move probabilities returned are proportional
to visit counts N(s,a) (optionally with a temperature parameter), which
is what self-play training targets are built from.
"""

from __future__ import annotations
import math
from typing import Optional

import numpy as np
import torch
import chess

from encoding import encode_board, legal_move_mask


class MCTSNode:
    __slots__ = ("parent", "move", "prior", "children", "visit_count",
                 "value_sum", "board", "is_expanded")

    def __init__(self, parent: Optional["MCTSNode"], move: Optional[chess.Move],
                 prior: float, board: chess.Board):
        self.parent = parent
        self.move = move            # move that led to this node (None for root)
        self.prior = prior          # P(s,a) from the network, set at expansion time
        self.children: dict[int, "MCTSNode"] = {}  # policy_index -> child node
        self.visit_count = 0
        self.value_sum = 0.0
        self.board = board          # the resulting board state at this node
        self.is_expanded = False

    def q_value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def is_leaf(self) -> bool:
        return not self.is_expanded


class MCTS:
    def __init__(self, model, device: str = "cpu", c_puct: float = 1.5,
                 num_simulations: int = 200, dirichlet_alpha: float = 0.3,
                 dirichlet_epsilon: float = 0.25):
        """
        model: a ChessNet (or compatible) in eval mode.
        c_puct: exploration constant.
        num_simulations: simulations per move-search call.
        dirichlet_alpha/epsilon: root exploration noise, applied only
            when `add_root_noise=True` is passed to `run` (self-play);
            disabled for pure inference/play against humans.
        """
        self.model = model
        self.device = device
        self.c_puct = c_puct
        self.num_simulations = num_simulations
        self.dirichlet_alpha = dirichlet_alpha
        self.dirichlet_epsilon = dirichlet_epsilon

    @torch.no_grad()
    def _evaluate(self, board: chess.Board) -> tuple[np.ndarray, float, dict[int, chess.Move]]:
        """Run the network on `board`, return (legal-move priors indexed by
        policy index restricted to legal moves, value, index->move map)."""
        planes = encode_board(board)
        x = torch.from_numpy(planes).unsqueeze(0).to(self.device)
        policy_logits, value = self.model(x)
        policy_logits = policy_logits.squeeze(0).cpu().numpy()
        value = value.item()

        mask, index_to_move = legal_move_mask(board)
        # mask illegal moves, then softmax over the legal subset only
        masked_logits = np.where(mask > 0, policy_logits, -1e9)
        max_logit = masked_logits.max()
        exp = np.exp(masked_logits - max_logit) * mask
        total = exp.sum()
        priors = exp / total if total > 0 else mask / max(mask.sum(), 1)

        return priors, value, index_to_move

    def _expand(self, node: MCTSNode) -> float:
        """Expand a leaf node: evaluate with the network, create children.
        Returns the leaf's value (from the perspective of the player to
        move at `node`)."""
        board = node.board
        outcome = board.outcome(claim_draw=True)
        if outcome is not None:
            # terminal node: no children, value is the actual game result
            if outcome.winner is None:
                return 0.0
            return 1.0 if outcome.winner == board.turn else -1.0

        priors, value, index_to_move = self._evaluate(board)
        for idx, move in index_to_move.items():
            child_board = board.copy(stack=False)
            child_board.push(move)
            node.children[idx] = MCTSNode(parent=node, move=move,
                                           prior=float(priors[idx]), board=child_board)
        node.is_expanded = True
        return value

    def _select_child(self, node: MCTSNode) -> tuple[int, MCTSNode]:
        best_score = -float("inf")
        best_idx, best_child = None, None
        sqrt_total = math.sqrt(node.visit_count)
        for idx, child in node.children.items():
            u = self.c_puct * child.prior * sqrt_total / (1 + child.visit_count)
            score = -child.q_value() + u  # negate: child.Q is from child's-turn perspective
            if score > best_score:
                best_score, best_idx, best_child = score, idx, child
        return best_idx, best_child

    def run(self, root_board: chess.Board, add_root_noise: bool = False) -> tuple[MCTSNode, dict[int, float]]:
        """
        Run `num_simulations` simulations from `root_board`.
        Returns (root_node, visit_probs) where visit_probs maps
        policy_index -> N(root, a) / sum(N(root, .)).
        """
        root = MCTSNode(parent=None, move=None, prior=1.0, board=root_board.copy(stack=False))
        self._expand(root)

        if add_root_noise and root.children:
            noise = np.random.dirichlet([self.dirichlet_alpha] * len(root.children))
            for (idx, child), n in zip(root.children.items(), noise):
                child.prior = (1 - self.dirichlet_epsilon) * child.prior + self.dirichlet_epsilon * n

        for _ in range(self.num_simulations):
            node = root
            path = [node]

            while node.is_expanded and node.children:
                idx, node = self._select_child(node)
                path.append(node)

            leaf_value = self._expand(node)

            # backup: value alternates sign as we go up (each ply flips
            # whose perspective the value is from)
            value = leaf_value
            for n in reversed(path):
                n.visit_count += 1
                n.value_sum += value
                value = -value

        total_visits = sum(child.visit_count for child in root.children.values())
        visit_probs = {idx: child.visit_count / total_visits for idx, child in root.children.items()} \
            if total_visits > 0 else {}
        return root, visit_probs

    def select_move(self, root_board: chess.Board, temperature: float = 1.0,
                     add_root_noise: bool = False) -> tuple[chess.Move, dict[int, float], float]:
        """
        Full move-selection helper for self-play / play endpoints.

        temperature: >0 samples proportional to N^(1/T); temperature=0
            (or very small) picks the most-visited move deterministically.
        Returns (chosen_move, visit_probs, root_value_estimate).
        """
        root, visit_probs = self.run(root_board, add_root_noise=add_root_noise)
        if not visit_probs:
            raise ValueError("No legal moves from this position (game is over).")

        indices = list(visit_probs.keys())
        if temperature < 1e-3:
            best_idx = max(indices, key=lambda i: visit_probs[i])
        else:
            visits = np.array([root.children[i].visit_count for i in indices], dtype=np.float64)
            scaled = visits ** (1.0 / temperature)
            probs = scaled / scaled.sum()
            best_idx = np.random.choice(indices, p=probs)

        chosen_move = root.children[best_idx].move
        root_value = root.q_value()
        return chosen_move, visit_probs, root_value
