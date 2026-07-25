import { useCallback, useEffect, useState } from "react";
import type { HealthResponse } from "../types";
import { API_BASE } from "../lib/config";

interface HealthState {
  data: HealthResponse | null;
  loading: boolean;
  error: string | null;
}

export function useHealth() {
  const [state, setState] = useState<HealthState>({ data: null, loading: true, error: null });

  const check = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = (await response.json()) as HealthResponse;
      setState({ data, loading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setState({ data: null, loading: false, error: message });
    }
  }, []);

  useEffect(() => {
    void check();
  }, [check]);

  return { ...state, recheck: check };
}
