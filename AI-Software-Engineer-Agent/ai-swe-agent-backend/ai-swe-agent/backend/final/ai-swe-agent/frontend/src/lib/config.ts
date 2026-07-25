// Single source of truth for where the backend lives. Both the /health
// fetch and the /ws/agent WebSocket derive from this one value so there's
// never a case where they're pointed at different hosts.

const rawBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** e.g. "http://localhost:8000" (trailing slash stripped) */
export const API_BASE = rawBase.replace(/\/+$/, "");

/** Same host, ws(s):// scheme — e.g. "ws://localhost:8000" */
export const WS_BASE = API_BASE.replace(/^http/, "ws");
