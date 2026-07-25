# Frontend — Agent Forge

React + TypeScript + Tailwind v4 + Vite. Chat/timeline on the left, live
code + terminal on the right, streamed from the backend over WebSocket.

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local   # only needed if the backend isn't on localhost:8000
npm run dev
```

Opens on `http://localhost:5173` — this exact origin must match
`backend/.env`'s `ALLOWED_ORIGINS`, since the backend's CORS config only
accepts requests from there by default.

## What's where

```
src/
├── App.tsx                     top-level layout: header, health banner, two panels
├── types.ts                    wire-format types, mirrors backend/app/schemas.py
├── lib/config.ts               resolves API_BASE / WS_BASE from VITE_API_BASE_URL
├── hooks/
│   ├── useHealth.ts             polls GET /health, exposes a manual recheck()
│   └── useAgentSocket.ts        owns the WebSocket: connect/reconnect, send task,
│                                 derive status + latest code/stdout/stderr from events
└── components/
    ├── HealthBanner.tsx         surfaces "Ollama not reachable" / missing models up front
    ├── EventFeed.tsx            left-panel timeline, one card per agent event
    ├── TaskInput.tsx            the textarea + "Build it" control
    ├── WorkspacePanel.tsx       right-panel shell: attempt pips, status, Code/Terminal tabs
    ├── AttemptPips.tsx          ●●○○ — which debug attempt is in flight
    ├── CodeView.tsx             line-numbered code view with a lightweight custom
    │                             Python highlighter (no Shiki/Prism dependency)
    └── TerminalView.tsx         stdout/stderr, terminal-styled
```

## Build

```bash
npm run build     # tsc -b (type-check) && vite build
npm run lint       # oxlint
```

Both are part of how this was verified before shipping — see the top-level
README for details.

## Notes on the design

Dark, low-chroma "workshop" background rather than pure black — this is a
tool people will stare at for a while, not a landing page. Each agent role
(Planner/Coder/Executor/Reviewer) gets its own accent color used
consistently across the timeline and tabs, since telling them apart at a
glance is load-bearing here, not decorative. Fonts are self-hosted via
`@fontsource` (IBM Plex Sans for UI, IBM Plex Mono for anything that's
actual code or log output) rather than pulled from a CDN — consistent with
the project's own "everything stays local" premise.

## Known limitations

- No mid-run cancel: the backend doesn't support aborting a run in
  progress, so the input just stays disabled until success/failure/error.
- If the WebSocket drops mid-run, the hook reconnects but that specific run
  is lost — start a new task once reconnected.
- The Python highlighter in `CodeView.tsx` is a lightweight regex
  tokenizer, not a real parser — triple-quoted strings and some escaping
  edge cases won't highlight perfectly.
