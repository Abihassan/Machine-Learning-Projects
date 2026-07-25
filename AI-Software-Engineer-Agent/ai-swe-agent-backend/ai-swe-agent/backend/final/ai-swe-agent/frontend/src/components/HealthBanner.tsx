import { AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";
import type { HealthResponse } from "../types";

interface HealthBannerProps {
  data: HealthResponse | null;
  loading: boolean;
  error: string | null;
  onRecheck: () => void;
}

export function HealthBanner({ data, loading, error, onRecheck }: HealthBannerProps) {
  if (loading && !data) {
    return (
      <div className="border-b border-line bg-surface px-4 py-2 text-xs text-text-dim">
        Checking Ollama and the sandbox…
      </div>
    );
  }

  if (error || !data) {
    return (
      <Banner tone="bad" onRecheck={onRecheck}>
        Can&rsquo;t reach the backend at all. Is <code className="font-mono">uvicorn app.main:app</code> running on
        port 8000?
      </Banner>
    );
  }

  if (!data.ollama_reachable) {
    return (
      <Banner tone="bad" onRecheck={onRecheck}>
        Ollama isn&rsquo;t reachable. Run <code className="font-mono">ollama serve</code>, then recheck.
      </Banner>
    );
  }

  if (data.missing_models.length > 0) {
    return (
      <Banner tone="warn" onRecheck={onRecheck}>
        Missing model{data.missing_models.length > 1 ? "s" : ""}: {data.missing_models.join(", ")} — run{" "}
        <code className="font-mono">ollama pull {data.missing_models[0]}</code>, then recheck.
      </Banner>
    );
  }

  return (
    <div className="flex items-center justify-between gap-3 border-b border-line bg-surface px-4 py-2 text-xs text-text-dim">
      <span className="flex items-center gap-1.5">
        <CheckCircle2 className="h-3.5 w-3.5 text-good" aria-hidden="true" />
        Ollama connected · {data.required_models.length} models ready
      </span>
      {data.executor_backend === "subprocess" && (
        <span className="flex items-center gap-1.5 text-executor">
          <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
          Running without a Docker sandbox — generated code executes directly on this machine.
        </span>
      )}
    </div>
  );
}

interface BannerProps {
  tone: "bad" | "warn";
  children: ReactNode;
  onRecheck: () => void;
}

function Banner({ tone, children, onRecheck }: BannerProps) {
  const toneClass = tone === "bad" ? "border-bad/40 bg-bad/10 text-bad" : "border-executor/40 bg-executor/10 text-executor";
  return (
    <div className={`flex items-center justify-between gap-3 border-b px-4 py-2 text-xs ${toneClass}`}>
      <span className="flex items-center gap-1.5">
        <AlertTriangle className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        {children}
      </span>
      <button
        type="button"
        onClick={onRecheck}
        className="flex shrink-0 items-center gap-1 rounded border border-current/30 px-2 py-1 hover:bg-current/10"
      >
        <RefreshCw className="h-3 w-3" aria-hidden="true" /> Recheck
      </button>
    </div>
  );
}
