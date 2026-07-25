const WATCHED_PATHS = ["data/", "src/models/"];

export default function Settings() {
  return (
    <div>
      <header className="mb-6">
        <h1 className="text-lg font-semibold text-ink">Settings</h1>
        <p className="text-sm text-muted mt-0.5">
          Pipeline behavior is configured through your repo's{" "}
          <code className="font-mono text-xs bg-raised px-1.5 py-0.5 rounded">config.yaml</code>.
        </p>
      </header>

      <div className="space-y-4 max-w-2xl">
        <section className="rounded-lg border border-line bg-surface p-4">
          <p className="text-xs uppercase tracking-wide text-muted mb-3">Webhook endpoint</p>
          <div className="flex items-center gap-2 font-mono text-sm">
            <span className="px-1.5 py-0.5 rounded bg-raised text-signal text-xs">POST</span>
            <code className="text-ink">/api/webhooks/git</code>
          </div>
          <p className="text-xs text-muted mt-2">
            Point your GitHub or GitLab repo's push webhook at this path on your deployed backend.
          </p>
        </section>

        <section className="rounded-lg border border-line bg-surface p-4">
          <p className="text-xs uppercase tracking-wide text-muted mb-3">Watched paths</p>
          <p className="text-sm text-muted mb-3">
            A push only triggers a pipeline run when it changes files under one of these paths.
          </p>
          <ul className="space-y-2">
            {WATCHED_PATHS.map((p) => (
              <li key={p} className="flex items-center gap-2 font-mono text-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-link" />
                {p}
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-lg border border-line bg-surface p-4">
          <p className="text-xs uppercase tracking-wide text-muted mb-3">config.yaml reference</p>
          <pre className="font-mono text-xs text-ink/80 bg-raised rounded-md p-3 overflow-x-auto">
{`model:
  source: local              # local | huggingface
  architecture: CustomCNN
  hf_model_id: distilbert-base-uncased

training:
  epochs: 5
  batch_size: 32
  learning_rate: 0.001
  val_split: 0.2

evaluation:
  precision_threshold: 0.85`}
          </pre>
        </section>
      </div>
    </div>
  );
}
