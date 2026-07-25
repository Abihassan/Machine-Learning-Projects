"""
Minimal manual test client for the /ws/agent endpoint — lets you exercise
the full backend end-to-end (real Ollama, real Docker sandbox) before the
React frontend exists.

Usage (from the backend/ directory, with the server already running):
    python scripts/test_client.py "write a function that checks if a number is prime, then test it on 2..50"

If no task is given, a small default task is used.
"""

import asyncio
import json
import sys

import websockets


async def main(task: str) -> None:
    uri = "ws://localhost:8000/ws/agent"
    async with websockets.connect(uri, max_size=None) as ws:
        await ws.send(json.dumps({"task": task}))
        while True:
            raw = await ws.recv()
            event = json.loads(raw)
            if event["type"] == "done":
                print("\n--- run complete ---")
                break
            if event["type"] == "error":
                print(f"\n!!! error: {event['content']}")
                break
            header = f"[{event['agent']}:{event['type']} it={event.get('iteration', 0)}]"
            print(f"\n{header}\n{event['content']}")


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Write a function that reverses a linked list, with a small demo."
    asyncio.run(main(task))
