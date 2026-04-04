import os
import time

from agent_private_i.core.models import new_task
from agent_private_i.core.orchestrator import Orchestrator
from agent_private_i.core.planner import Planner
from agent_private_i.core.queue import InMemoryQueue
from agent_private_i.core.router import Router
from agent_private_i.core.state_store import FileStateStore
from agent_private_i.core.verifier import Verifier
from agent_private_i.workers.coder import CoderWorker
from agent_private_i.workers.research_bot import ResearchBotWorker
from agent_private_i.workers.senior_dev import SeniorDevWorker
from agent_private_i.workers.verifier import VerifierWorker


def build_system():
    # Use PostgresStateStore and RedisQueue when environment variables are set,
    # otherwise fall back to file + in-memory queue for local demos.
    os.environ.get("REDIS_URL")
    pg_dsn = os.environ.get("PG_DSN")

    if pg_dsn:
        try:
            from agent_private_i.core.state_store import PostgresStateStore

            store = PostgresStateStore(pg_dsn)
        except Exception:
            store = FileStateStore()
    else:
        store = FileStateStore()

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


def demo_run():
    # prefer Redis if configured
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            from agent_private_i.core.queue import RedisQueue

            q = RedisQueue(url=redis_url)
        except Exception:
            q = InMemoryQueue()
    else:
        q = InMemoryQueue()
    orch, store = build_system()

    t = new_task(
        goal="Research bristoltalks.com and report whether the live site is online",
        inputs={"query": "bristoltalks.com status"},
        success_criteria=["research_notes_present", "verified_online_status"],
    )

    # serialize to dict for queue
    q.enqueue(t)

    print("Enqueued task:", t.task_id)

    # Dequeue and run
    payload = q.dequeue(block_seconds=2)
    if not payload:
        print("No tasks found")
        return

    # run_task expects dict-like payload
    start = time.time()
    result = orch.run_task(payload)
    elapsed = time.time() - start
    print(
        "Task completed:",
        result.get("task_id"),
        "status=",
        result.get("status"),
        f"(elapsed={elapsed:.2f}s)",
    )
    print("History:")
    for h in result.get("history", []):
        print(" -", h)


if __name__ == "__main__":
    demo_run()
