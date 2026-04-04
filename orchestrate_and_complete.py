#!/usr/bin/env python
r"""Create a new orchestrator run and automatically submit required tool outputs.

Flow:
 - Read dev JWT from `.token.txt` (fallback to creating one via auth.create_jwt if missing).
 - POST to `http://127.0.0.1:8081/orchestrate` with a sample message to start a run.
 - Extract `thread_id` and `run_id` from the response.
 - Poll the run using `AssistantsAgent.wait_for_run_completion` until it reaches
   `requires_action` (or terminal state).
 - If `required_action.submit_tool_outputs` is present, synthesize outputs and
   call `AssistantsAgent.submit_tool_outputs` to continue the run, then poll to
   completion and save the final run JSON to `run_final_auto.json`.

Usage:
  .venv\Scripts\python.exe orchestrate_and_complete.py

Note: Requires `OPENAI_API_KEY` in environment for Assistant API calls and the
local `orchestrator` service running on port 8081.
"""

import json
import os
import sys
import time
from typing import Any, Optional

import requests

from assistants_agent import AssistantsAgent


def read_token() -> Optional[str]:
    if os.path.exists(".token.txt"):
        # try several encodings to handle PowerShell/Windows BOM variants
        for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
            try:
                with open(".token.txt", encoding=enc) as f:
                    return f.read().strip()
            except Exception:
                continue
        # fallback: read raw bytes and decode latin-1
        try:
            with open(".token.txt", "rb") as f:
                return f.read().decode("latin-1").strip()
        except Exception:
            return None
    return None


def get_base_url() -> str:
    return (os.environ.get("ORCHESTRATOR_URL") or "http://127.0.0.1:8082").rstrip("/")


# Orchestration schedule for a small production workflow (engraving & laser cutting)
# This can be dumped to a file with the `--dump-orchestration` CLI flag.
ORCHESTRATION_SCHEDULE = {
    "Design Agent": {
        "schedule": "Mon, Wed 09:00-11:00",
        "task": "Gather client requirements, develop custom design drafts, and prepare vector files for laser cutting/engraving.",
    },
    "Material Preparation Agent": {
        "schedule": "Mon, Wed 11:00-13:00",
        "task": "Select and prepare wood sheets, clean surfaces, and ensure materials are ready for laser processing according to design specifications.",
    },
    "Laser Operator Agent": {
        "schedule": "Tue, Thu 09:00-12:00",
        "task": "Set up the laser machine, upload design files, perform test cuts/engravings, and execute final laser cutting and engraving jobs.",
    },
    "Quality Control Agent": {
        "schedule": "Tue, Thu 12:00-13:00",
        "task": "Inspect finished pieces for accuracy, quality, and adherence to client requirements; report issues for correction.",
    },
    "Finishing & Packaging Agent": {
        "schedule": "Fri 09:00-12:00",
        "task": "Sand and finish products as needed, apply protective coatings, and package completed pieces for delivery.",
    },
    "Project Coordinator Agent": {
        "schedule": "Daily 08:30-09:00",
        "task": "Oversee task schedules, communicate with all agents, update clients on progress, and adjust schedules as needed.",
    },
}


def dump_orchestration_to_file(path: str = "orchestration_schedule.json") -> None:
    """Write the `ORCHESTRATION_SCHEDULE` to a JSON file for inspection or importing."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ORCHESTRATION_SCHEDULE, f, indent=2, ensure_ascii=False)
        print(f"Orchestration schedule written to {path}")
    except Exception as exc:
        print(f"Failed to write orchestration schedule: {exc}")


def start_orchestrator_run(token: Optional[str], session_id: str = "dev-session") -> dict[str, Any]:
    url = f"{get_base_url()}/orchestrate"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "session_id": session_id,
        "message": "Please classify and run a small test orchestration",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def require_orchestrator_alive() -> None:
    """Fail fast if orchestrator is not responding on /health."""
    url = f"{get_base_url()}/health"
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            raise RuntimeError(f"health check returned {data}")
    except Exception as exc:  # broad: we want to exit quickly with guidance
        print(f"Orchestrator health check failed at {url}: {exc}")
        sys.exit(1)


def synthesize_output(call: dict[str, Any]) -> str:
    try:
        # support both dict-like and SDK object shapes
        if hasattr(call, "get"):
            func = call.get("function") or {}
            args_text = (
                func.get("arguments")
                if isinstance(func, dict)
                else getattr(func, "arguments", None)
            )
        else:
            func = getattr(call, "function", None)
            args_text = getattr(func, "arguments", None)

        if isinstance(args_text, str):
            payload = json.loads(args_text)
        elif isinstance(args_text, dict):
            payload = args_text
        else:
            payload = {}

        path = (
            payload.get("path")
            or payload.get("file")
            or payload.get("filename")
            or payload.get("uri")
            or "<unknown>"
        )
        return f"Auto-classification for {path}: file classified; recommend Alex M."
    except Exception:
        return "Auto tool output: processed."


def submit_for_run(
    agent: AssistantsAgent, thread_id: str, run_id: str, run_obj: dict[str, Any]
) -> dict[str, Any]:
    # run_obj may be a dict or an SDK object; handle both.
    if hasattr(run_obj, "get"):
        required = run_obj.get("required_action") or {}
    else:
        required = getattr(run_obj, "required_action", None) or {}

    if hasattr(required, "get"):
        submit = required.get("submit_tool_outputs") or {}
    else:
        submit = getattr(required, "submit_tool_outputs", None) or {}

    if hasattr(submit, "get"):
        tool_calls = submit.get("tool_calls") or []
    else:
        tool_calls = getattr(submit, "tool_calls", None) or []
    if not tool_calls:
        print("No tool calls to submit.")
        return run_obj

    outputs: list[dict[str, Any]] = []
    for call in tool_calls:
        # support SDK objects and dicts
        cid = None
        if hasattr(call, "get"):
            cid = call.get("id") or call.get("tool_call_id")
        else:
            cid = getattr(call, "id", None) or getattr(call, "tool_call_id", None)

        out_text = synthesize_output(call)
        outputs.append({"tool_call_id": cid, "output": out_text})

    print(f"Submitting {len(outputs)} tool outputs...")
    res = agent.submit_tool_outputs(thread_id=thread_id, run_id=run_id, tool_outputs=outputs)
    return res


def main() -> None:
    token = read_token()
    # Support quick dump of the built-in orchestration schedule and exit.
    if "--dump-orchestration" in sys.argv:
        dump_orchestration_to_file()
        return
    require_orchestrator_alive()
    print("Starting orchestrator run...")
    resp = start_orchestrator_run(token)
    # Save response for inspection
    with open("run_response_auto.json", "w", encoding="utf-8") as f:
        json.dump(resp, f, indent=2)

    # Attempt to find thread_id & run_id
    result = resp.get("result") or {}
    run = result.get("raw") or {}
    run_id = result.get("id") or run.get("id")
    thread_id = run.get("thread_id")
    if not run_id or not thread_id:
        print("Could not extract run_id/thread_id from orchestrator response.")
        print(json.dumps(resp, indent=2))
        return

    print(f"Run created: {run_id} (thread {thread_id})")

    agent = AssistantsAgent()

    # Poll until requires_action or terminal
    print("Polling run until requires_action or terminal...")
    max_wait = 120
    elapsed = 0
    poll_interval = 1.0
    current = None
    while elapsed < max_wait:
        current = agent.retrieve_run(thread_id=thread_id, run_id=run_id)
        status = getattr(current, "status", None) or current.get("status")
        if status in ("requires_action", "completed", "failed", "cancelled", "expired"):
            break
        time.sleep(poll_interval)
        elapsed += poll_interval

    print("Run status:", status)
    # Convert run object to dict if it's an SDK object
    run_obj = current if isinstance(current, dict) else getattr(current, "__dict__", current)

    if status == "requires_action":
        submit_for_run(agent, thread_id, run_id, run_obj)
        # After submit, poll again to completion
        print("Submitted tool outputs, polling to completion...")
        final = agent.wait_for_run_completion(
            thread_id=thread_id, run_id=run_id, poll_interval=1.0, max_wait_seconds=120
        )
        # Save final run
        final_dict = final if isinstance(final, dict) else getattr(final, "__dict__", final)
        with open("run_final_auto.json", "w", encoding="utf-8") as f:
            json.dump(final_dict, f, indent=2, default=str)
        print("Final run status:", getattr(final, "status", None) or final_dict.get("status"))
    else:
        # Save whatever we got
        with open("run_final_auto.json", "w", encoding="utf-8") as f:
            json.dump(run_obj, f, indent=2, default=str)
        print("Run ended with status:", status)


if __name__ == "__main__":
    main()
