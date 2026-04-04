import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

TaskStatus = Literal["queued", "running", "blocked", "failed", "done"]
StepStatus = Literal["pending", "running", "failed", "done"]


@dataclass
class Step:
    step_id: str
    title: str
    assigned_role: str
    input: dict[str, Any] = field(default_factory=dict)
    output: Optional[dict[str, Any]] = None
    status: StepStatus = "pending"
    error: Optional[str] = None


@dataclass
class Task:
    task_id: str
    goal: str
    inputs: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    success_criteria: list[str] = field(default_factory=list)
    status: TaskStatus = "queued"
    attempts: int = 0
    steps: list[Step] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


def new_task(goal: str, inputs=None, constraints=None, success_criteria=None) -> Task:
    return Task(
        task_id=str(uuid.uuid4()),
        goal=goal,
        inputs=inputs or {},
        constraints=constraints or {},
        success_criteria=success_criteria or [],
    )
