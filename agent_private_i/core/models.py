from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional
import time
import uuid

TaskStatus = Literal["queued", "running", "blocked", "failed", "done"]
StepStatus = Literal["pending", "running", "failed", "done"]


@dataclass
class Step:
    step_id: str
    title: str
    assigned_role: str
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    status: StepStatus = "pending"
    error: Optional[str] = None


@dataclass
class Task:
    task_id: str
    goal: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    status: TaskStatus = "queued"
    attempts: int = 0
    steps: List[Step] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


def new_task(goal: str, inputs=None, constraints=None, success_criteria=None) -> Task:
    return Task(
        task_id=str(uuid.uuid4()),
        goal=goal,
        inputs=inputs or {},
        constraints=constraints or {},
        success_criteria=success_criteria or [],
    )
