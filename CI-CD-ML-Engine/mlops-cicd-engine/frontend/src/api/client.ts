import type { PipelineRun, RegisteredModel } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listPipelineRuns: () => request<PipelineRun[]>("/api/pipelines"),
  getPipelineRun: (id: string) => request<PipelineRun>(`/api/pipelines/${id}`),
  listModels: () => request<RegisteredModel[]>("/api/models"),
};

/** Poll a fetcher every `intervalMs` — used to fake "real-time" run status. */
export function pollEvery<T>(
  fetcher: () => Promise<T>,
  onData: (data: T) => void,
  intervalMs = 4000
): () => void {
  let cancelled = false;
  const tick = async () => {
    try {
      const data = await fetcher();
      if (!cancelled) onData(data);
    } catch {
      // swallow — dashboard keeps showing last-known state on transient errors
    }
  };
  tick();
  const id = setInterval(tick, intervalMs);
  return () => {
    cancelled = true;
    clearInterval(id);
  };
}
