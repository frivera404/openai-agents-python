from agent_private_i.workers.base import WorkerBase
import os


class VerifierWorker(WorkerBase):
    role = "verifier"

    def run(self, step: dict, task_payload: dict) -> dict:
        """Attempt verification via MCP test-runner when available, otherwise apply simple heuristics.

        Returns {'verified': bool, ...}.
        """
        task_id = task_payload.get("task_id")
        # Try MCP test-runner
        try:
            from agent_private_i.tools.mcp_tool import MCPTool

            m = MCPTool(os.environ.get("MCP_BASE_URL"))
            payload = {"task_id": task_id, "step": step}
            resp = m.call("tools/run_tests", payload)
            if resp.get("error"):
                return {"verified": False, "error": resp.get("error")}
            return {"verified": bool(resp.get("verified", True)), "mcp": resp}
        except Exception:
            # Heuristic fallback: require that the step has non-empty output or artifact_path
            output = step.get("output") or {}
            ok = False
            if isinstance(output, dict):
                if output.get("verified") is True:
                    ok = True
                elif output.get("artifact_path") or output.get("result") or output.get("notes"):
                    ok = True
            return {"verified": ok, "reason": "heuristic"}
