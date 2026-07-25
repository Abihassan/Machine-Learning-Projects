import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, pollEvery } from "../api/client";
import type { PipelineRun } from "../types";
import StatusBadge from "../components/StatusBadge";
import MetricsChart from "../components/MetricsChart";
import { CardSkeleton } from "../components/Skeleton";

export default function PipelineDetail() {
  const { runId } = useParams<{ runId: string }>();
  const [run, setRun] = useState<PipelineRun | null>(null);

  useEffect(() => {
    if (!runId) return;
    return pollEvery(() => api.getPipelineRun(runId), setRun, 4000);
  }, [runId]);

  if (!run) {
    return (
      <div className="space-y-4">
        <div className="h-4 w-48 rounded bg-raised animate-pulse" />
        <CardSkeleton />
      </div>
    );
  }

  const metric = run.metrics[0];

  return (
    <div>
      <Link to="/" className="text-xs text-muted hover:text-link">← Back to pipeline runs</Link>

      <header className="mt-3 mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-lg font-semibold text-ink font-mono">{run.commit_hash.slice(0, 12)}</h1>
          <p className="text-sm text-muted mt-1">{run.commit_message}</p>
          <p className="text-xs text-muted mt-1 font-mono">
            {run.repo} · {run.branch} · triggered by {run.triggered_path}
          </p>
        </div>
        <StatusBadge status={run.status} />
      </header>

      {run.status === "failed" && run.error_message && (
        <div className="mb-6 rounded-lg border border-danger/30 bg-danger/5 p-4">
          <p className="text-xs uppercase tracking-wide text-danger mb-1">Run failed</p>
          <pre className="text-xs text-ink/80 font-mono whitespace-pre-wrap">{run.error_message}</pre>
        </div>
      )}

      {metric ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-lg border border-line bg-surface p-4">
            <p className="text-xs uppercase tracking-wide text-muted mb-4">
              Precision vs. baseline threshold
            </p>
            <MetricsChart metric={metric} />
          </div>

          <div className="rounded-lg border border-line bg-surface p-4 space-y-4">
            <p className="text-xs uppercase tracking-wide text-muted">Run summary</p>
            <dl className="space-y-3 text-sm">
              <Row label="Precision" value={metric.precision.toFixed(3)} accent={metric.beat_baseline} />
              <Row label="Recall" value={metric.recall.toFixed(3)} />
              <Row label="F1 score" value={metric.f1_score.toFixed(3)} />
              <Row
                label="Baseline precision"
                value={metric.baseline_precision != null ? metric.baseline_precision.toFixed(3) : "—"}
              />
              <Row label="Epochs" value={String(metric.epoch_count)} />
              <Row
                label="Checkpoint"
                value={metric.beat_baseline ? "Saved — new best" : "Not saved — did not beat baseline"}
              />
            </dl>
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted">
          {run.status === "running" ? "Training in progress — metrics will appear when evaluation finishes." : "No metrics recorded for this run."}
        </p>
      )}
    </div>
  );
}

function Row({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="flex items-center justify-between border-b border-line pb-2 last:border-0 last:pb-0">
      <dt className="text-muted">{label}</dt>
      <dd className={`font-mono ${accent ? "text-success" : "text-ink"}`}>{value}</dd>
    </div>
  );
}
