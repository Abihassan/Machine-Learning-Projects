import { useEffect, useState } from "react";
import { api, pollEvery } from "../api/client";
import type { RegisteredModel } from "../types";
import { CardSkeleton } from "../components/Skeleton";

function SourceTag({ source }: { source: RegisteredModel["source"] }) {
  return (
    <span
      className={`font-mono text-[11px] px-1.5 py-0.5 rounded border ${
        source === "local"
          ? "text-link border-link/30 bg-link/5"
          : "text-signal border-signal/30 bg-signal/5"
      }`}
    >
      {source === "local" ? "local" : "hugging face"}
    </span>
  );
}

export default function ModelRegistry() {
  const [models, setModels] = useState<RegisteredModel[] | null>(null);

  useEffect(() => pollEvery(api.listModels, setModels, 6000), []);

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-lg font-semibold text-ink">Model registry</h1>
        <p className="text-sm text-muted mt-0.5">
          Every checkpoint saved when a run's precision beat the previous best.
        </p>
      </header>

      {models === null && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {models?.length === 0 && (
        <div className="rounded-lg border border-line bg-surface p-10 text-center text-sm text-muted">
          No models registered yet. A checkpoint is saved the first time a run's precision
          beats the baseline threshold.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {models?.map((m) => (
          <div key={m.id} className="rounded-lg border border-line bg-surface p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-mono text-sm text-ink">{m.architecture_or_hf_id}</p>
                <p className="text-xs text-muted mt-0.5">version {m.version}</p>
              </div>
              <SourceTag source={m.source} />
            </div>

            <div className="mt-4 flex items-end justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-wide text-muted">Top precision</p>
                <p className="font-mono text-xl text-success">{m.top_precision.toFixed(3)}</p>
              </div>
              {m.is_active && (
                <span className="font-mono text-[11px] px-1.5 py-0.5 rounded border border-success/30 bg-success/5 text-success">
                  active
                </span>
              )}
            </div>

            {m.commit_hash && (
              <p className="mt-3 pt-3 border-t border-line text-[11px] text-muted font-mono">
                from commit {m.commit_hash.slice(0, 10)}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
