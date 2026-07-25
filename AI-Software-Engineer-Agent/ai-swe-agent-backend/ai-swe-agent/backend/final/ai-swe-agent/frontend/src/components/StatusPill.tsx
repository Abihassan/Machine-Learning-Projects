import type { RunStatus } from "../types";

const LABEL: Record<RunStatus, string> = {
  idle: "Ready",
  running: "Running",
  success: "Success",
  failed: "Gave up",
  error: "Error",
};

const DOT_CLASS: Record<RunStatus, string> = {
  idle: "bg-text-dim",
  running: "bg-executor animate-pulse",
  success: "bg-good",
  failed: "bg-bad",
  error: "bg-bad",
};

export function StatusPill({ status }: { status: RunStatus }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 text-xs font-medium text-text-dim">
      <span className={`h-1.5 w-1.5 rounded-full ${DOT_CLASS[status]}`} aria-hidden="true" />
      {LABEL[status]}
    </span>
  );
}
