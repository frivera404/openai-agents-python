from agent_private_i.workers.base import WorkerBase
import os
import json
from pathlib import Path


class CoderWorker(WorkerBase):
    role = "coder"

    def run(self, step: dict, task_payload: dict) -> dict:
        """Attempt code generation via MCP if configured, otherwise write a local placeholder artifact.

        Returns a dict with at least `result` and `artifact_path` when possible.
        """
        task_id = task_payload.get("task_id") or "unknown"
        # Try MCP-based codegen
        try:
            from agent_private_i.tools.mcp_tool import MCPTool

            m = MCPTool(os.environ.get("MCP_BASE_URL"))
            payload = {"task_id": task_id, "step": step, "inputs": task_payload.get("inputs", {})}
            resp = m.call("tools/codegen", payload)
            if resp.get("error"):
                raise RuntimeError(resp.get("error"))

            # Persist artifact if returned
            artifact = resp.get("artifact") or resp
            art_dir = Path(".agent_state") / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            filename = art_dir / f"{task_id}_coder_artifact.json"
            with open(filename, "w", encoding="utf-8") as f:
                if isinstance(artifact, (str, bytes)):
                    f.write(str(artifact))
                else:
                    json.dump(artifact, f, indent=2)

            return {"result": "codegen_via_mcp", "mcp": resp, "artifact_path": str(filename)}
        except Exception as e:
            # Fallback: write a minimal placeholder implementation file
            art_dir = Path(".agent_state") / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            filename = art_dir / f"{task_id}_coder_placeholder.py"
            content = (
                f"# Placeholder code for task {task_id}\n"
                f"# Step: {step.get('step_id')} - {step.get('title')}\n\n"
                "def placeholder():\n"
                "    return 'placeholder implementation'\n"
            )
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return {"result": "placeholder_written", "artifact_path": str(filename), "error": str(e)}
