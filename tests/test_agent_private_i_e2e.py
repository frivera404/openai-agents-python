import os
import sys

# Ensure the project root is on sys.path when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_private_i.core.models import new_task
from agent_private_i.core.orchestrator import Orchestrator
from agent_private_i.core.planner import Planner
from agent_private_i.core.router import Router
from agent_private_i.core.state_store import FileStateStore
from agent_private_i.core.verifier import Verifier
from agent_private_i.workers.coder import CoderWorker
from agent_private_i.workers.research_bot import ResearchBotWorker
from agent_private_i.workers.senior_dev import SeniorDevWorker
from agent_private_i.workers.verifier import VerifierWorker


def build_system_for_test(state_dir: str):
    store = FileStateStore(path=state_dir)
    workers = {
        "research_bot": ResearchBotWorker(),
        "coder": CoderWorker(),
        "senior_dev": SeniorDevWorker(),
        "verifier": VerifierWorker(),
    }
    router = Router(workers)
    planner = Planner()
    verifier = Verifier()
    orch = Orchestrator(router, planner, verifier, store, max_attempts=3)
    return orch, store


def test_orchestrator_completes_task(tmp_path):
    state_dir = str(tmp_path / "agent_state")
    orch, store = build_system_for_test(state_dir)

    t = new_task(
        goal="Verify example site status",
        inputs={"query": "ctdatenight.com status"},
        success_criteria=["research_notes_present", "verified_online_status"],
    )

    payload = t.__dict__.copy()
    result = orch.run_task(payload)

    assert result.get("status") == "done"
    assert all(s.get("status") == "done" for s in result.get("steps", []))

    # persisted state should exist
    loaded = store.load(result["task_id"])
    assert loaded is not None
