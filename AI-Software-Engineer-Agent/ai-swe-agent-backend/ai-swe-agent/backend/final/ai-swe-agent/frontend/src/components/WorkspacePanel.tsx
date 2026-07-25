import { useState, type ReactNode } from "react";
import type { RunStatus } from "../types";
import { AttemptPips } from "./AttemptPips";
import { StatusPill } from "./StatusPill";
import { CodeView } from "./CodeView";
import { TerminalView } from "./TerminalView";

type Tab = "code" | "terminal";

interface WorkspacePanelProps {
  code: string;
  stdout: string;
  stderr: string;
  attempt: number;
  maxAttempts: number;
  status: RunStatus;
}

export function WorkspacePanel({ code, stdout, stderr, attempt, maxAttempts, status }: WorkspacePanelProps) {
  const [tab, setTab] = useState<Tab>("code");
  const hasError = Boolean(stderr);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg border border-line bg-ink">
      <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-2.5">
        <div className="flex items-center gap-3">
          <AttemptPips attempt={attempt} maxAttempts={maxAttempts} status={status} />
          <span className="text-xs text-text-dim">
            attempt {attempt} of {maxAttempts}
          </span>
        </div>
        <StatusPill status={status} />
      </div>

      <div className="flex border-b border-line px-2">
        <TabButton active={tab === "code"} onClick={() => setTab("code")}>
          Code
        </TabButton>
        <TabButton active={tab === "terminal"} onClick={() => setTab("terminal")} flagged={hasError}>
          Terminal
        </TabButton>
      </div>

      <div className="min-h-0 flex-1">
        {tab === "code" ? <CodeView code={code} attempt={attempt} /> : <TerminalView stdout={stdout} stderr={stderr} />}
      </div>
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
  flagged?: boolean;
}

function TabButton({ active, onClick, children, flagged }: TabButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative px-3 py-2 text-[13px] font-medium transition-colors ${
        active ? "text-text" : "text-text-dim hover:text-text"
      }`}
    >
      {children}
      {flagged && !active && (
        <span className="absolute right-0.5 top-1.5 h-1.5 w-1.5 rounded-full bg-bad" aria-hidden="true" />
      )}
      {active && <span className="absolute inset-x-3 -bottom-px h-0.5 rounded-full bg-coder" aria-hidden="true" />}
    </button>
  );
}
