import copy
import time
from agent_private_i.core.planner import Planner
from agent_private_i.core.router import Router
from agent_private_i.core.verifier import Verifier


class Orchestrator:
    def __init__(self, router: Router, planner: Planner, verifier: Verifier, state_store, max_attempts: int = 5):
        self.router = router
        self.planner = planner
        self.verifier = verifier
        self.state_store = state_store
        self.max_attempts = max_attempts

    def run_task(self, task_payload: dict) -> dict:
        task_id = task_payload["task_id"]
        task_payload["status"] = "running"
        task_payload.setdefault("attempts", 0)

        if not task_payload.get("steps"):
            steps = [s.__dict__ for s in self.planner.make_plan(task_payload)]
            task_payload["steps"] = steps

        while task_payload["attempts"] < self.max_attempts:
            self.state_store.save(task_id, task_payload["status"], task_payload)

            pending = next((s for s in task_payload["steps"] if s["status"] == "pending"), None)
            if not pending:
                ok, msg = self.verifier.verify_task(task_payload)
                if ok:
                    task_payload["status"] = "done"
                    task_payload.setdefault("history", []).append({"event": "task_done", "msg": msg, "ts": time.time()})
                    self.state_store.save(task_id, task_payload["status"], task_payload)
                    return task_payload

                task_payload["attempts"] += 1
                task_payload.setdefault("history", []).append({"event": "verify_failed", "msg": msg, "ts": time.time()})
                task_payload["steps"].append({
                    "step_id": f"fix-{task_payload['attempts']}",
                    "title": f"Fix verification issue: {msg}",
                    "assigned_role": "senior_dev",
                    "input": {"reason": msg},
                    "output": None,
                    "status": "pending",
                    "error": None,
                })
                continue

            pending["status"] = "running"
            self.state_store.save(task_id, "running", task_payload)

            try:
                worker = self.router.pick(pending["assigned_role"])
                out = worker.run(copy.deepcopy(pending), copy.deepcopy(task_payload))
                pending["output"] = out
                pending["status"] = "done"
                task_payload.setdefault("history", []).append({"event": "step_done", "step": pending["step_id"], "ts": time.time()})
            except Exception as e:
                pending["error"] = str(e)
                pending["status"] = "failed"
                task_payload["attempts"] += 1
                task_payload.setdefault("history", []).append({"event": "step_failed", "step": pending["step_id"], "err": str(e), "ts": time.time()})

                task_payload["steps"].append({
                    "step_id": f"recover-{task_payload['attempts']}",
                    "title": f"Recover from error in step {pending['step_id']}",
                    "assigned_role": "senior_dev",
                    "input": {"error": str(e), "failed_step": pending},
                    "output": None,
                    "status": "pending",
                    "error": None,
                })

        task_payload["status"] = "failed"
        self.state_store.save(task_id, "failed", task_payload)
        return task_payload
