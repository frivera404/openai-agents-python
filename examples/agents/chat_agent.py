#!/usr/bin/env python3
"""
A minimal Chat Agent that routes user messages to local tools (engraving agents)
using simple intent matching and maintains lightweight state across a session.

This is intended as an example of building a chat workflow with custom logic
and tools inside this repository.
"""
from typing import Any, Dict, Optional
import json

from examples.agents import engraving_agents as tools


class ChatAgent:
    def __init__(self) -> None:
        # store last artifacts created during the session
        self.state: Dict[str, Any] = {}

    def handle_message(self, message: str) -> Dict[str, Any]:
        """Process a user message, call tools as needed, and return a structured reply.

        Strategy (very small rule-based policy):
        - If message mentions 'design' -> call `create_design`.
        - If message mentions 'material' or 'prepare' -> call `prepare_materials`.
        - If message mentions 'run' or 'laser' -> call `run_laser_job` using latest design/batch.
        - If message mentions 'qc' or 'quality' -> call `qc_check` using latest job.
        - If message mentions 'finish' or 'package' -> call `finish_and_package`.
        - Otherwise, return a conversational acknowledgement.
        """
        m = message.lower()
        if "design" in m:
            # extract a short requirements string (naive)
            req = message
            res_text = tools.create_design(req, style="standard")
            try:
                res = json.loads(res_text)
                self.state["design_file"] = res.get("design_file")
            except Exception:
                res = {"error": res_text}
            return {"action": "create_design", "result": res}

        if "material" in m or "prepare" in m:
            # naive parsing for count and material
            material = "birch"
            sheets = 1
            # look for a number
            for word in m.split():
                if word.isdigit():
                    sheets = int(word)
                    break
            res_text = tools.prepare_materials(material=material, sheets=sheets)
            res = json.loads(res_text)
            self.state["batch_id"] = res.get("batch_id")
            return {"action": "prepare_materials", "result": res}

        if "run" in m or "laser" in m:
            design_file = self.state.get("design_file")
            batch_id = self.state.get("batch_id")
            if not design_file or not batch_id:
                return {
                    "action": "run_laser_job",
                    "error": "missing design_file or batch_id; create design and prepare materials first",
                }
            res_text = tools.run_laser_job(design_file, batch_id, test_run=False)
            res = json.loads(res_text)
            self.state["job_id"] = res.get("job_id")
            return {"action": "run_laser_job", "result": res}

        if "qc" in m or "quality" in m or "inspect" in m:
            job_id = self.state.get("job_id")
            if not job_id:
                return {"action": "qc_check", "error": "no job_id available; run the laser job first"}
            res_text = tools.qc_check(job_id)
            res = json.loads(res_text)
            self.state["qc"] = res
            return {"action": "qc_check", "result": res}

        if "finish" in m or "package" in m:
            job_id = self.state.get("job_id")
            if not job_id:
                return {"action": "finish_and_package", "error": "no job_id available"}
            res_text = tools.finish_and_package(job_id, finish_type="oil", box_size="medium")
            res = json.loads(res_text)
            self.state["package"] = res
            return {"action": "finish_and_package", "result": res}

        # default reply
        return {"action": "reply", "text": "I can help with design, materials, laser run, QC, and finishing. Try: 'create design', 'prepare materials', 'run laser'."}


def create_agent() -> ChatAgent:
    return ChatAgent()


if __name__ == "__main__":
    a = ChatAgent()
    print(a.handle_message("Please create a design for a round keychain with ACME logo"))
