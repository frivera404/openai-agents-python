import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[str]
    role: str = "free"
    scopes: list[str] = Field(default_factory=list)


class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    agent_state: dict[str, Any] = Field(default_factory=dict)
    memory_scope: str = "private"
    rate_limit: str = "tier_based"


class IntentRoute(BaseModel):
    route_to: str
    confidence: float
