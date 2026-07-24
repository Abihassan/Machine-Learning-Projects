import { useCallback, useEffect, useMemo, useState } from "react";
import { Chess, type Square } from "chess.js";
import { Chessboard } from "react-chessboard";
import { requestAiMove, checkHealth, ApiError } from "./apiClient";
import "./App.css";

type GameStatus = "playing" | "checkmate" | "stalemate" | "draw" | "game-over";

function describeStatus(chess: Chess): GameStatus {
  if (chess.isCheckmate()) return "checkmate";
  if (chess.isStalemate()) return "stalemate";
  if (chess.isDraw()) return "draw";
  if (chess.isGameOver()) return "game-over";
  return "playing";
}

export default function App() {
  const [game, setGame] = useState(() => new Chess());
  const [fen, setFen] = useState(game.fen());
  const [status, setStatus] = useState<GameStatus>("playing");
  const [aiThinking, setAiThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [lastAiEval, setLastAiEval] = useState<number | null>(null);
  const [moveHistory, setMoveHistory] = useState<string[]>([]);

  // Human always plays White, AI always plays Black, for simplicity.
  const humanColor = "white" as const;

  useEffect(() => {
    checkHealth().then(setBackendOnline);
  }, []);

  const syncFromGame = useCallback((g: Chess) => {
    setFen(g.fen());
    setStatus(describeStatus(g));
    setMoveHistory(g.history());
  }, []);

  const requestAiTurn = useCallback(
    async (g: Chess) => {
      if (g.isGameOver()) return;
      setAiThinking(true);
      setError(null);
      try {
        const result = await requestAiMove(g.fen());
        g.move(result.move_uci, { strict: false }); // UCI-format move (e.g. "e2e4", "e7e8q")
        setLastAiEval(result.value_estimate);
        syncFromGame(g);
      } catch (e) {
        setError(e instanceof ApiError ? e.message : "Unexpected error requesting AI move.");
      } finally {
        setAiThinking(false);
      }
    },
    [syncFromGame]
  );

  const onPieceDrop = useCallback(
    (sourceSquare: Square, targetSquare: Square): boolean => {
      if (aiThinking || game.isGameOver() || game.turn() !== "w") return false;

      const gameCopy = new Chess(game.fen());
      let move;
      try {
        move = gameCopy.move({
          from: sourceSquare,
          to: targetSquare,
          promotion: "q", // auto-promote to queen for simplicity; extend with a picker if desired
        });
      } catch {
        return false; // illegal move, snap piece back
      }
      if (move === null) return false;

      setGame(gameCopy);
      syncFromGame(gameCopy);
      setError(null);

      // Hand the turn to the AI after the human's move completes.
      void requestAiTurn(gameCopy);

      return true;
    },
    [aiThinking, game, requestAiTurn, syncFromGame]
  );

  const resetGame = useCallback(() => {
    const fresh = new Chess();
    setGame(fresh);
    syncFromGame(fresh);
    setLastAiEval(null);
    setError(null);
  }, [syncFromGame]);

  const statusMessage = useMemo(() => {
    switch (status) {
      case "checkmate":
        return `Checkmate — ${game.turn() === "w" ? "Black" : "White"} wins.`;
      case "stalemate":
        return "Stalemate — draw.";
      case "draw":
        return "Draw.";
      case "game-over":
        return "Game over.";
      default:
        return aiThinking ? "AI is thinking…" : game.turn() === "w" ? "Your move." : "Waiting for AI…";
    }
  }, [status, game, aiThinking]);

  return (
    <div className="app">
      <header className="header">
        <h1>Chess AI Engine</h1>
        <p className={`backend-status ${backendOnline ? "online" : "offline"}`}>
          Backend: {backendOnline === null ? "checking…" : backendOnline ? "online" : "offline"}
        </p>
      </header>

      <main className="main">
        <div className="board-container">
          <Chessboard
            position={fen}
            onPieceDrop={onPieceDrop}
            boardOrientation={humanColor}
            arePiecesDraggable={!aiThinking && status === "playing"}
            customBoardStyle={{
              borderRadius: "8px",
              boxShadow: "0 8px 24px rgba(0, 0, 0, 0.35)",
            }}
          />
        </div>

        <aside className="sidebar">
          <div className="status-card">
            <p className="status-message">{statusMessage}</p>
            {lastAiEval !== null && (
              <p className="eval">
                AI evaluation: <strong>{lastAiEval.toFixed(2)}</strong>{" "}
                <span className="eval-hint">(from AI's perspective, -1 = losing, +1 = winning)</span>
              </p>
            )}
            {error && <p className="error">{error}</p>}
          </div>

          <div className="history-card">
            <h2>Move history</h2>
            <ol className="move-list">
              {moveHistory.map((san, i) => (
                <li key={i}>{san}</li>
              ))}
            </ol>
          </div>

          <button className="reset-button" onClick={resetGame}>
            New game
          </button>
        </aside>
      </main>
    </div>
  );
}
