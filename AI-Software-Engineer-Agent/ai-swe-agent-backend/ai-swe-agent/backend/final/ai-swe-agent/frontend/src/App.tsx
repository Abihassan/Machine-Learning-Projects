import { useHealth } from "./hooks/useHealth";
import { useAgentSocket } from "./hooks/useAgentSocket";
import { HealthBanner } from "./components/HealthBanner";
import { EventFeed } from "./components/EventFeed";
import { TaskInput } from "./components/TaskInput";
import { WorkspacePanel } from "./components/WorkspacePanel";

const DEFAULT_MAX_ATTEMPTS = 4;

function App() {
  const health = useHealth();
  const agent = useAgentSocket();

  const maxAttempts = health.data?.max_debug_iterations ?? DEFAULT_MAX_ATTEMPTS;
  const isRunning = agent.status === "running";

  return (
    <div className="flex h-screen flex-col bg-ink text-text">
      <header className="flex items-center justify-between border-b border-line px-5 py-3">
        <div className="flex items-baseline gap-2">
          <h1 className="font-mono text-base font-semibold tracking-tight">Agent Forge</h1>
          <span className="text-xs text-text-dim">local AI software engineer</span>
        </div>
        <span
          className={`h-2 w-2 rounded-full ${agent.isConnected ? "bg-good" : "bg-bad"}`}
          title={agent.isConnected ? "Connected to backend" : "Disconnected — reconnecting…"}
        />
      </header>

      <HealthBanner data={health.data} loading={health.loading} error={health.error} onRecheck={health.recheck} />

      <main className="flex min-h-0 flex-1 flex-col gap-3 p-3 md:flex-row">
        <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-line bg-ink md:w-2/5 md:flex-none">
          <div className="min-h-0 flex-1 overflow-y-auto">
            <EventFeed events={agent.events} />
          </div>
          <TaskInput disabled={isRunning || !agent.isConnected} onSubmit={agent.sendTask} />
        </section>

        <section className="min-h-0 flex-1">
          <WorkspacePanel
            code={agent.latestCode}
            stdout={agent.latestStdout}
            stderr={agent.latestStderr}
            attempt={agent.attempt}
            maxAttempts={maxAttempts}
            status={agent.status}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
