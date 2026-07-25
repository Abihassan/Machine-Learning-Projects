import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, pollEvery } from "../api/client";
import type { PipelineRun } from "../types";
import StatusBadge from "../components/StatusBadge";
import { TableRowSkeleton } from "../components/Skeleton";

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function formatDuration(seconds: number | null): string {
  if (seconds == null) return "—";
  if (seconds < 60) return `${seconds.toFixed(0)}s`;
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}

export default function Dashboard() {
  const [runs, setRuns] = useState<PipelineRun[] | null>(null);

  useEffect(() => pollEvery(api.listPipelineRuns, setRuns, 4000), []);

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-lg font-semibold text-ink">Pipeline runs</h1>
        <p className="text-sm text-muted mt-0.5">
          Triggered automatically when a commit touches{" "}
          <code className="font-mono text-xs bg-raised px-1.5 py-0.5 rounded">data/</code> or{" "}
          <code className="font-mono text-xs bg-raised px-1.5 py-0.5 rounded">src/models/</code>
        </p>
      </header>

      <div className="rounded-lg border border-line bg-surface overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-left text-xs text-muted uppercase tracking-wide">
              <th className="px-4 py-3 font-medium">Commit</th>
              <th className="px-4 py-3 font-medium">Branch</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Precision</th>
              <th className="px-4 py-3 font-medium">Duration</th>
            </tr>
          </thead>
          <tbody>
            {runs === null &&
              Array.from({ length: 4 }).map((_, i) => <TableRowSkeleton key={i} />)}

            {runs?.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-muted text-sm">
                  No pipeline runs yet. Push a commit touching{" "}
                  <span className="font-mono text-xs">data/</span> or{" "}
                  <span className="font-mono text-xs">src/models/</span> to trigger one.
                </td>
              </tr>
            )}

            {runs?.map((run) => {
              const metric = run.metrics[0];
              return (
                <tr key={run.id} className="border-b border-line last:border-0 group relative">
                  {/* git-log rail */}
                  <td className="px-4 py-3 relative">
                    <div className="absolute left-[18px] top-0 bottom-0 w-px bg-line group-first:top-1/2 group-last:bottom-1/2" />
                    <Link to={`/runs/${run.id}`} className="relative flex items-center gap-3 hover:text-link">
                      <span
                        className={`relative z-10 w-2 h-2 rounded-full ${
                          run.status === "success"
                            ? "bg-success"
                            : run.status === "failed"
                            ? "bg-danger"
                            : run.status === "running"
                            ? "bg-signal animate-pulse_dot"
                            : "bg-muted"
                        }`}
                      />
                      <div>
                        <div className="font-mono text-xs text-ink">{run.commit_hash.slice(0, 10)}</div>
                        <div className="text-xs text-muted max-w-xs truncate">{run.commit_message}</div>
                      </div>
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-muted font-mono text-xs">{run.branch}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={run.status} />
                    <div className="text-[11px] text-muted mt-0.5">{timeAgo(run.started_at)}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {metric ? (
                      <span className={metric.beat_baseline ? "text-success" : "text-ink"}>
                        {metric.precision.toFixed(3)}
                      </span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-muted font-mono text-xs">
                    {formatDuration(run.duration_seconds)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
