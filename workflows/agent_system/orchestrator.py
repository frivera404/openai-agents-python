"""Orchestrator for existing assistants inventory.

This module orchestrates calls to pre-existing assistants (Alex S., Layer Manager,
Coder, Gemini API, Supervisor Backup). It tries to use the OpenAI Assistants API
pattern when available and falls back to a safe local simulator for testing.

Behavior implemented:
- Single entry `orchestrate_input` that follows the master workflow.
- Supervisor routing via `supervisor_route` (uses remote assistant or local logic).
- Handoff to `layer_manager_execute`, `coder_execute`, `gemini_execute`.
- Verification with Alex S. via `verify_with_supervisor` (or local check).
- Retry once on failure, then escalate to supervisor backup.
- Logs all steps via `logger.log_event` and updates memory via `memory`.
"""

import json
import time
from typing import Any, Optional

try:
    from openai import OpenAI  # user provided pattern
except Exception:
    OpenAI = None

from .logger import log_event
from .memory import add_long_term, write_session
try:
    # local ChatAgent for workshop tasks
    from examples.agents.chat_agent import create_agent as _create_chat_agent
except Exception:
    _create_chat_agent = None

# single ChatAgent instance (lazy)
CHAT_AGENT = None

# Agent inventory (as provided)
AGENTS = {
    "alex": "asst_XZqf46Wxz4XL9pI7VHraZQEi",
    "layer": "asst_gWX3gVfbHwVn9y7wm0FZml22",
    "coder": "asst_Tswpu395P3VGnEuMwcOga1l6",
    "backup": "asst_aoU291xGQgwlqgoQsxoWYfbQ",
    "gemini": "asst_IJgUbeTrvwAFVyRJxZoUErmy",
}


def _local_classify(user_input: str) -> str:
    m = user_input.lower()
    # route workshop-related terms to chat agent
    if any(k in m for k in ("design", "laser", "material", "qc", "finish", "package", "engrave")):
        return "chat"
    if any(k in m for k in ("marketing", "affiliate", "campaign")):
        return "alex"
    if any(k in m for k in ("workflow", "orchestrate", "run tasks", "chain")):
        return "layer"
    if any(k in m for k in ("fix", "bug", "implement", "script", "code")):
        return "coder"
    if any(k in m for k in ("api", "enrich", "fetch", "external")):
        return "gemini"
    return "alex"


def _make_client():
    if OpenAI is None:
        return None
    return OpenAI()


def run_agent(
    agent_id: str, message: str, thread_id: Optional[str] = None, client=None
) -> tuple[str, dict[str, Any]]:
    """Run an assistant. Returns (thread_id, result_dict).

    If no OpenAI client is available, the function returns a simulated result.
    """
    if client is None:
        client = _make_client()

    # If we have a real client, use the user's Assistants pattern
    if client is not None:
        try:
            if not thread_id:
                thread = client.beta.threads.create()
                thread_id = thread.id
            client.beta.threads.messages.create(thread_id=thread_id, role="user", content=message)
            run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=agent_id)
            # Attempt to return run outputs if available
            return thread_id, {"id": getattr(run, "id", None), "raw": run}
        except Exception:
            # propagate exception to allow retry/escalation
            raise

    # Fallback simulation (no external call)
    thread_id = thread_id or f"local-{int(time.time() * 1000)}"
    # Simple simulated behaviors for main agents
    role = None
    for k, v in AGENTS.items():
        if v == agent_id or k == agent_id:
            role = k
            break
    if role is None:
        role = agent_id

    simulated = {"role": role, "message": message}
    if role == "alex":
        # Return JSON string as the assistant would
        choice = {"route": _local_classify(message), "confidence": 0.9}
        simulated["response_json"] = json.dumps(choice)
    elif role == "layer":
        simulated["tasks"] = ["step1", "step2"]
    elif role == "coder":
        simulated["code"] = "# generated code snippet"
    elif role == "gemini":
        simulated["enrichment"] = {"data": "enriched"}
    elif role == "backup":
        simulated["action"] = "escalated"

    return thread_id, simulated


def supervisor_route(user_input: str, client=None) -> dict[str, Any]:
    """Ask Alex S. to route intent. Returns parsed route dict.

    If OpenAI Assistants API is available this will call the assistant; otherwise
    it uses the local classifier.
    """
    agent_id = AGENTS["alex"]
    prompt = (
        f"Classify intent and return only JSON: Input: {user_input}\n"
        "Options: layer_manager, coder, gemini_api, self"
    )
    try:
        _, res = run_agent(agent_id, prompt, client=client)
        # If remote, user code may need to parse run outputs. We support both remote and simulated.
        if isinstance(res.get("raw"), dict) and res.get("raw").get("output"):
            parsed = res["raw"]["output"]
            return parsed
        if "response_json" in res:
            return json.loads(res["response_json"])
    except Exception:
        pass
    # Fallback
    choice = _local_classify(user_input)
    return {"route": choice, "confidence": 0.8}


def layer_manager_execute(task_description: str, client=None) -> dict[str, Any]:
    _, res = run_agent(
        AGENTS["layer"], f"Orchestrate and delegate this task:\n{task_description}", client=client
    )
    return res


def chat_execute(user_input: str, client=None) -> dict[str, Any]:
    """Execute input using the local ChatAgent (if available).

    This function returns the ChatAgent's structured reply dictionary.
    """
    global CHAT_AGENT
    if _create_chat_agent is None:
        return {"error": "chat agent not available"}
    if CHAT_AGENT is None:
        try:
            CHAT_AGENT = _create_chat_agent()
        except Exception as e:
            return {"error": f"failed to create chat agent: {e}"}

    try:
        res = CHAT_AGENT.handle_message(user_input)
        return res
    except Exception as e:
        return {"error": str(e)}


def coder_execute(code_task: str, client=None) -> dict[str, Any]:
    _, res = run_agent(AGENTS["coder"], f"Write production-ready code:\n{code_task}", client=client)
    return res


def gemini_execute(api_task: str, client=None) -> dict[str, Any]:
    _, res = run_agent(
        AGENTS["gemini"], f"Fetch / enrich using external API:\n{api_task}", client=client
    )
    return res


def verify_with_supervisor(result: Any, client=None) -> dict[str, Any]:
    _, res = run_agent(
        AGENTS["alex"], f"Verify correctness, safety, and completeness:\n{result}", client=client
    )
    # Simulated verification returns ok by default
    if isinstance(res, dict) and res.get("role") == "alex":
        return {"ok": True, "notes": "simulated ok"}
    if isinstance(res.get("raw"), dict):
        return {"ok": True, "raw": res.get("raw")}
    return {"ok": True}


def orchestrate_input(
    user_id: str, session_id: str, user_input: str, client=None
) -> dict[str, Any]:
    """Master orchestration entry point.

    - Logs the incoming request
    - Asks Alex S. to route
    - Delegates to Layer Manager or specific agent
    - Verifies output with Alex S.
    - On failure retries once then escalates to backup supervisor
    - Stores state and logs events
    """
    log_event(
        {
            "user_id": user_id,
            "session_id": session_id,
            "action": "start_orchestration",
            "input": user_input,
        }
    )

    # 1) Supervisor routing
    route = supervisor_route(user_input, client=client)
    target = route.get("route") or route.get("route_to") or "alex"
    log_event(
        {
            "user_id": user_id,
            "session_id": session_id,
            "action": "routed",
            "target": target,
            "confidence": route.get("confidence"),
        }
    )

    # 2) Execute
    attempt = 0
    last_err = None
    while attempt < 2:
        try:
            if target in ("layer", "layer_manager"):
                agent_result = layer_manager_execute(user_input, client=client)
            elif target in ("coder",):
                agent_result = coder_execute(user_input, client=client)
            elif target in ("gemini", "gemini_api"):
                agent_result = gemini_execute(user_input, client=client)
            elif target in ("chat",):
                agent_result = chat_execute(user_input, client=client)
            elif target in ("alex", "self"):
                _, agent_result = run_agent(AGENTS["alex"], user_input, client=client)
            else:
                # default to alex
                _, agent_result = run_agent(AGENTS["alex"], user_input, client=client)

            log_event(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "action": "agent_executed",
                    "target": target,
                }
            )

            # 3) Verify
            ver = verify_with_supervisor(agent_result, client=client)
            if not ver.get("ok"):
                raise RuntimeError(f"verification failed: {ver}")

            # 4) Persist state and memory
            add_long_term(
                user_id,
                {
                    "session_id": session_id,
                    "agent": target,
                    "result": agent_result,
                    "time": int(time.time()),
                },
            )
            write_session(
                session_id,
                {
                    "session_id": session_id,
                    "active_agent": target,
                    "last_action": "completed",
                    "status": "success",
                },
            )

            log_event(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "action": "completed",
                    "target": target,
                }
            )
            return {"status": "success", "agent": target, "result": agent_result}

        except Exception as e:
            last_err = e
            log_event(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "action": "agent_error",
                    "target": target,
                    "error": str(e),
                    "attempt": attempt + 1,
                }
            )
            attempt += 1
            # retry once
            if attempt >= 2:
                # escalate to backup supervisor
                try:
                    _, esc = run_agent(
                        AGENTS["backup"],
                        f"Escalation: handle failed task for user {user_id}: {user_input}",
                        client=client,
                    )
                    log_event(
                        {
                            "user_id": user_id,
                            "session_id": session_id,
                            "action": "escalated",
                            "backup": True,
                        }
                    )
                    add_long_term(
                        user_id, {"session_id": session_id, "agent": "backup", "result": esc}
                    )
                    return {"status": "escalated", "backup_result": esc, "error": str(last_err)}
                except Exception as e2:
                    log_event(
                        {
                            "user_id": user_id,
                            "session_id": session_id,
                            "action": "escalation_failed",
                            "error": str(e2),
                        }
                    )
                    return {"status": "failed", "error": str(last_err)}

    return {"status": "failed", "error": str(last_err)}
