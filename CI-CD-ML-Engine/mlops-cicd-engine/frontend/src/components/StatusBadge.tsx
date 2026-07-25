import type { RunStatus } from "../types";

const STYLES: Record<RunStatus, { dot: string; text: string; label: string; pulse?: boolean }> = {
  queued: { dot: "bg-muted", text: "text-muted", label: "Queued" },
  running: { dot: "bg-signal", text: "text-signal", label: "Running", pulse: true },
  success: { dot: "bg-success", text: "text-success", label: "Success" },
  failed: { dot: "bg-danger", text: "text-danger", label: "Failed" },
};

export default function StatusBadge({ status }: { status: RunStatus }) {
  const s = STYLES[status];
  return (
    <span className={`inline-flex items-center gap-1.5 font-mono text-xs ${s.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot} ${s.pulse ? "animate-pulse_dot" : ""}`} />
      {s.label}
    </span>
  );
}
