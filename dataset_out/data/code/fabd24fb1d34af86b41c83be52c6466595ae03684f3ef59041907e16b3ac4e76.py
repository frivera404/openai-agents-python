import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so scripts can be run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_private_i.core.models import new_task

local_dir = Path("local_tasks")
local_dir.mkdir(exist_ok=True)

t = new_task(
    goal="Check whether ctdatenight.com is serving a homepage and save summary",
    inputs={"url": "https://ctdatenight.com"},
    success_criteria=["summary_present", "status_200"],
)

p = local_dir / (t.task_id + ".json")
with open(p, "w", encoding="utf-8") as fh:
    json.dump(t.__dict__, fh, default=str)

print("Wrote:", p)
