import type { AgentEvent } from "../types";

const AGENT_META: Record<AgentEvent["agent"], { label: string; text: string; border: string }> = {
  planner: { label: "Planner", text: "text-planner", border: "border-planner" },
  coder: { label: "Coder", text: "text-coder", border: "border-coder" },
  executor: { label: "Executor", text: "text-executor", border: "border-executor" },
  reviewer: { label: "Reviewer", text: "text-reviewer", border: "border-reviewer" },
  system: { label: "System", text: "text-text-dim", border: "border-line" },
};

const SHOWS_ATTEMPT_BADGE: AgentEvent["type"][] = ["code", "review", "stdout", "stderr"];

function summarize(event: AgentEvent): string {
  switch (event.type) {
    case "plan":
    case "review":
    case "success":
    case "failure":
    case "error":
      return event.content;
    case "code":
      return event.iteration === 0
        ? "Wrote a first draft — see the Code tab."
        : "Revised the script based on the Reviewer's notes — see the Code tab.";
    case "stdout": {
      const trimmed = event.content.trim();
      if (trimmed === "" || trimmed === "(no stdout)") {
        return "Ran it — produced no output. Check the Terminal tab.";
      }
      const firstLine = trimmed.split("\n")[0]!.slice(0, 90);
      return `Ran it. Output started with: ${firstLine} — full output in the Terminal tab.`;
    }
    case "stderr":
      return "Hit an error — see the Terminal tab for the full traceback.";
    case "done":
      return "";
    default:
      return event.content;
  }
}

function EventCard({ event }: { event: AgentEvent }) {
  const meta = AGENT_META[event.agent];
  const isGood = event.type === "success";
  const isBad = event.type === "failure" || event.type === "error";
  const accentText = isGood ? "text-good" : isBad ? "text-bad" : meta.text;
  const accentBorder = isGood ? "border-good" : isBad ? "border-bad" : meta.border;

  return (
    <li className={`animate-fade-in rounded-md border-l-2 bg-surface px-3 py-2.5 ${accentBorder}`}>
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className={`font-mono text-[11px] font-medium uppercase tracking-wide ${accentText}`}>
          {meta.label}
        </span>
        {event.iteration > 0 && SHOWS_ATTEMPT_BADGE.includes(event.type) && (
          <span className="text-[11px] text-text-dim">attempt {event.iteration + 1}</span>
        )}
      </div>
      <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-text">{summarize(event)}</p>
    </li>
  );
}

export function EventFeed({ events }: { events: AgentEvent[] }) {
  const visible = events.filter((event) => event.type !== "done");

  if (visible.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="font-mono text-2xl text-line">{">"}_</p>
        <p className="text-sm text-text-dim">
          Describe what to build below. The Planner, Coder, and Reviewer will narrate their work
          here as it happens.
        </p>
      </div>
    );
  }

  return (
    <ol className="flex flex-col gap-2.5 p-3">
      {visible.map((event, index) => (
        <EventCard key={index} event={event} />
      ))}
    </ol>
  );
}
