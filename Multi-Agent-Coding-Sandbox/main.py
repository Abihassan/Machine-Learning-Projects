"""
main.py
========
Entry point. Example:

    python main.py "Build a full-stack to-do app with React frontend and FastAPI backend"

Flow:
  1. Build the PM -> Frontend/Backend -> QA crew (tasks.py).
  2. Kick it off (Crew.kickoff) — CrewAI runs tasks in dependency order,
     passing each Task's output into the next via `context=[...]`.
  3. Inspect output/qa_report.md. If it reports FAIL for a component,
     automatically spin up one corrective fix-pass task for that developer
     agent, then re-run just the QA check on that component.
  4. Print a final summary of everything written to ./output.
"""

import os
import sys
import json
import argparse
from datetime import datetime

from crewai import Crew, Process
from tasks import build_pipeline, build_fix_pass
from agents import OUTPUT_DIR, run_sandbox_tool


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Coding Sandbox")
    parser.add_argument("prompt", type=str, nargs="?",
                         default="Build a full-stack to-do list app with a React "
                                 "frontend and a FastAPI + SQLite backend.",
                         help="Natural-language description of the app to build.")
    parser.add_argument("--max-fix-passes", type=int, default=1,
                         help="How many automatic QA-driven fix iterations to allow.")
    args = parser.parse_args()

    print(f"\n{'='*70}\nMulti-Agent Coding Sandbox\n{'='*70}")
    print(f"User request: {args.prompt}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Started: {datetime.now().isoformat()}\n")

    try:
        agents, tasks = build_pipeline(args.prompt)
    except RuntimeError as e:
        # Most likely: local LLM not reachable (see llm_config.py)
        print(f"[FATAL] Could not initialize agents/LLMs: {e}")
        sys.exit(1)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,   # PM -> Frontend & Backend -> QA, in order
        verbose=True,
    )

    try:
        result = crew.kickoff()
    except Exception as e:
        print(f"[FATAL] Crew execution failed: {e}")
        print("Common causes: Ollama not running, model not pulled, or Docker "
              "daemon unreachable. Check llm_config.py and sandbox_manager.py.")
        sys.exit(1)

    print(f"\n{'='*70}\nInitial QA pass complete\n{'='*70}\n{result}\n")

    # ------------------------------------------------------------------
    # Feedback loop: read qa_report.md and, if failures are reported,
    # trigger a bounded number of corrective fix passes.
    # ------------------------------------------------------------------
    qa_report_path = os.path.join(OUTPUT_DIR, "qa_report.md")
    fix_passes_used = 0

    while fix_passes_used < args.max_fix_passes and os.path.exists(qa_report_path):
        with open(qa_report_path, "r", encoding="utf-8") as f:
            qa_text = f.read()

        failing_targets = []
        if "FAIL" in qa_text.upper() and "frontend" in qa_text.lower():
            failing_targets.append("frontend")
        if "FAIL" in qa_text.upper() and "backend" in qa_text.lower():
            failing_targets.append("backend")

        if not failing_targets:
            print("QA report shows no failures — build succeeded.")
            break

        print(f"\nQA reported failures in: {failing_targets}. "
              f"Running fix pass {fix_passes_used + 1}/{args.max_fix_passes}...\n")

        for target in failing_targets:
            _, fix_task = build_fix_pass(qa_text, target)
            fix_crew = Crew(agents=[fix_task.agent], tasks=[fix_task],
                             process=Process.sequential, verbose=True)
            fix_crew.kickoff()

            # Re-verify just this component in the sandbox directly (bypassing
            # the LLM for this check — we just need the raw pass/fail signal).
            run_cmd = ("npm install && npm run build" if target == "frontend"
                       else "pip install -r requirements.txt && python -c "
                            "\"import main\" ")
            verify_json = run_sandbox_tool.func(
                subdirectory=target, run_command=run_cmd,
                base_image="node:20-slim" if target == "frontend" else "python:3.11-slim",
            )
            print(f"Re-verification for {target}:\n{verify_json}\n")

        fix_passes_used += 1

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    print(f"\n{'='*70}\nDone. Generated project tree:\n{'='*70}")
    for root, _, files in os.walk(OUTPUT_DIR):
        level = root.replace(OUTPUT_DIR, "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        for fname in files:
            print(f"{indent}  {fname}")

    print(f"\nFull code available under: {os.path.abspath(OUTPUT_DIR)}")
    if os.path.exists(qa_report_path):
        print(f"QA report: {os.path.abspath(qa_report_path)}")


if __name__ == "__main__":
    main()
