/**
 * apiClient.ts
 * ------------
 * Thin typed wrapper around the FastAPI backend's /play endpoint.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface PlayResponse {
  move_uci: string;
  move_san: string;
  is_check: boolean;
  is_checkmate: boolean;
  is_stalemate: boolean;
  is_game_over: boolean;
  value_estimate: number;
  fen_after_move: string;
}

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

export async function requestAiMove(fen: string, numSimulations?: number): Promise<PlayResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen, num_simulations: numSimulations ?? null }),
    });
  } catch {
    throw new ApiError(
      "Couldn't reach the chess engine backend. Is it running on " + API_BASE_URL + "?"
    );
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse failure, fall back to statusText
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as PlayResponse;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
