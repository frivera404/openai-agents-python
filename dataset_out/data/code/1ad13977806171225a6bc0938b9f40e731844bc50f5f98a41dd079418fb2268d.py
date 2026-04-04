import json
import os
import sys
from typing import Any

"""Small helper to read `run_response.json`, poll the run via
`AssistantsAgent.wait_for_run_completion`, and write a JSON-friendly
`run_final.json` file.

This script is intentionally small and tolerant of SDK object shapes.
"""


def _read_run_response(path: str = "run_response.json") -> dict:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def main() -> None:
    try:
        r = _read_run_response()
    except Exception as e:
        print("Could not read run_response.json:", e)
        sys.exit(1)

    raw = r.get("result", {}).get("raw", {})
    thread_id = raw.get("thread_id")
    run_id = raw.get("id")
    if not thread_id or not run_id:
        print("No thread/run id found, exiting")
        sys.exit(1)

    try:
        from assistants_agent import AssistantsAgent
    except Exception as e:
        print("Could not import AssistantsAgent:", e)
        sys.exit(2)

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set; cannot poll remote run.")
        sys.exit(3)

    agent = AssistantsAgent()
    print("Polling run completion via OpenAI API...")
    run = agent.wait_for_run_completion(thread_id, run_id, poll_interval=2.0, max_wait_seconds=60)

    # Convert to JSON-friendly structure
    out: Any = run
    if hasattr(run, "to_dict"):
        try:
            out = run.to_dict()
        except Exception:
            out = getattr(run, "__dict__", str(run))
    else:
        out = getattr(run, "__dict__", run)

    with open("run_final.json", "w", encoding="utf-8") as f:
        try:
            json.dump(out, f, indent=2, default=str)
        except TypeError:
            f.write(str(out))

    print("Wrote run_final.json")
    print("Final status:", getattr(run, "status", None))


if __name__ == "__main__":
    main()
