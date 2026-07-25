import type { RunStatus } from "../types";

interface AttemptPipsProps {
  /** 1-indexed */
  attempt: number;
  maxAttempts: number;
  status: RunStatus;
}

/**
 * A physical row of dots for "attempt N of MAX" — this is a real, ordered
 * sequence (each retry is informed by the one before it), which is exactly
 * the case where a numbered/stepped indicator earns its place rather than
 * decorating a list that isn't actually sequential.
 */
export function AttemptPips({ attempt, maxAttempts, status }: AttemptPipsProps) {
  const total = Math.max(maxAttempts, attempt);
  const pips = Array.from({ length: total }, (_, i) => i + 1);

  return (
    <div className="flex items-center gap-1.5" role="img" aria-label={`Attempt ${attempt} of ${maxAttempts}`}>
      {pips.map((n) => {
        let className = "bg-line"; // not reached yet
        if (n < attempt) {
          className = "bg-text-dim"; // spent on an earlier attempt
        } else if (n === attempt) {
          if (status === "success") className = "bg-good";
          else if (status === "failed" || status === "error") className = "bg-bad";
          else if (status === "running") className = "bg-executor animate-pulse";
          else className = "bg-text-dim";
        }
        return <span key={n} className={`h-2 w-2 rounded-full transition-colors ${className}`} />;
      })}
    </div>
  );
}
