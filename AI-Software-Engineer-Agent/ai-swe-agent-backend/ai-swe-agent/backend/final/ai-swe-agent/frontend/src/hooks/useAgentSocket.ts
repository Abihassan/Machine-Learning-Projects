import { useCallback, useEffect, useRef, useState } from "react";
import type { AgentEvent, RunStatus } from "../types";
import { WS_BASE } from "../lib/config";

const RECONNECT_DELAY_MS = 2000;

export interface AgentRunState {
  events: AgentEvent[];
  status: RunStatus;
  isConnected: boolean;
  latestCode: string;
  latestStdout: string;
  latestStderr: string;
  /** 1-indexed, for display ("attempt 2 of 4") — the backend's own iteration counter is 0-indexed. */
  attempt: number;
}

const INITIAL_RUN_STATE: AgentRunState = {
  events: [],
  status: "idle",
  isConnected: false,
  latestCode: "",
  latestStdout: "",
  latestStderr: "",
  attempt: 1,
};

function applyEvent(prev: AgentRunState, event: AgentEvent): AgentRunState {
  const events = [...prev.events, event];
  const attempt = event.iteration + 1;

  switch (event.type) {
    case "code":
      // A new attempt just started — clear out the previous attempt's
      // terminal output so it can't be mistaken for this one's result.
      return { ...prev, events, latestCode: event.content, latestStdout: "", latestStderr: "", attempt };
    case "stdout":
      return { ...prev, events, latestStdout: event.content, attempt };
    case "stderr":
      return { ...prev, events, latestStderr: event.content, attempt };
    case "success":
      return { ...prev, events, status: "success" };
    case "failure":
      return { ...prev, events, status: "failed" };
    case "error":
      return { ...prev, events, status: "error" };
    case "done":
      return { ...prev, events };
    default:
      return { ...prev, events };
  }
}

export function useAgentSocket() {
  const [state, setState] = useState<AgentRunState>(INITIAL_RUN_STATE);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    const socket = new WebSocket(`${WS_BASE}/ws/agent`);
    socketRef.current = socket;

    socket.onopen = () => {
      setState((prev) => ({ ...prev, isConnected: true }));
    };

    socket.onmessage = (message) => {
      const parsed = JSON.parse(message.data as string) as AgentEvent;
      setState((prev) => applyEvent(prev, parsed));
    };

    socket.onclose = () => {
      setState((prev) => ({ ...prev, isConnected: false }));
      if (mountedRef.current) {
        reconnectTimerRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
      }
    };

    socket.onerror = () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      socketRef.current?.close();
    };
  }, [connect]);

  const sendTask = useCallback((task: string) => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    // Fresh run: keep the connection state, drop everything else.
    setState((prev) => ({ ...INITIAL_RUN_STATE, isConnected: prev.isConnected, status: "running" }));
    socket.send(JSON.stringify({ task }));
  }, []);

  return { ...state, sendTask };
}
