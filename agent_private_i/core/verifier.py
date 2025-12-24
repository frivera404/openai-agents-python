class Verifier:
    def verify_task(self, task_payload: dict) -> tuple[bool, str]:
        steps = task_payload.get("steps", [])
        if not steps:
            return False, "No steps exist"
        if any(s.get("status") != "done" for s in steps):
            return False, "Not all steps completed"
        return True, "All steps completed"
