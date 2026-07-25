// Mirrors backend/app/schemas.py exactly. If you change the wire format on
// one side, change it here too — nothing enforces this automatically across
// the language boundary.

export type EventType =
  | "plan"
  | "code"
  | "stdout"
  | "stderr"
  | "review"
  | "success"
  | "failure"
  | "error"
  | "done";

export type AgentName = "planner" | "coder" | "executor" | "reviewer" | "system";

export interface AgentEvent {
  type: EventType;
  agent: AgentName;
  content: string;
  iteration: number;
  ts?: string;
}

export interface HealthResponse {
  ollama_reachable: boolean;
  required_models: string[];
  missing_models: string[];
  executor_backend: "docker" | "subprocess";
  max_debug_iterations: number;
}

/** Derived client-side from the stream of AgentEvents — not sent by the backend directly. */
export type RunStatus = "idle" | "running" | "success" | "failed" | "error";
