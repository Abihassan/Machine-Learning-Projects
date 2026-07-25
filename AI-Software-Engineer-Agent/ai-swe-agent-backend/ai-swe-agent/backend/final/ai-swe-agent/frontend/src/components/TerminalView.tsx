import { EmptyPane } from "./EmptyPane";

interface TerminalViewProps {
  stdout: string;
  stderr: string;
}

export function TerminalView({ stdout, stderr }: TerminalViewProps) {
  if (!stdout && !stderr) {
    return <EmptyPane message="Output will appear here once the Executor runs the code." />;
  }

  return (
    <div className="h-full overflow-auto p-4 font-mono text-[13px] leading-6">
      {stdout && <pre className="whitespace-pre-wrap text-text">{stdout}</pre>}
      {stderr && (
        <pre className="mt-3 whitespace-pre-wrap border-t border-line pt-3 text-bad">{stderr}</pre>
      )}
    </div>
  );
}
