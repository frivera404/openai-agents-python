from agent_private_i.core.models import Step


class Planner:
    def make_plan(self, task_payload: dict) -> list[Step]:
        # Minimal plan; replace with LLM-based planning later
        return [
            Step(step_id="1", title="Research requirements", assigned_role="research_bot"),
            Step(step_id="2", title="Implement solution", assigned_role="coder"),
            Step(step_id="3", title="Verify completion", assigned_role="verifier"),
        ]
