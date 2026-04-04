"""Minimal FastAPI app exposing auth, session and chat endpoints for the agent workflow.

Endpoints:
- POST /auth/register
- POST /auth/login
- POST /session/init
- POST /chat/process
- POST /webhook/stripe
"""

from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from .auth import (
    authenticate_api_token,
    authenticate_email_password,
    create_jwt,
    init_session,
    oauth_fallback,
    register_user,
    verify_jwt,
)
from .logger import log_event
from .memory import read_session, write_session
from .models import User
from .orchestrator import orchestrate_input
from .tools import make_default_registry
from .verifier import Verifier

app = FastAPI(title="Agent Workflow API")

tools = make_default_registry()
verifier = Verifier()


class RegisterPayload(BaseModel):
    email: str
    password: str


class LoginPayload(BaseModel):
    email: Optional[str]
    password: Optional[str]
    oauth_provider: Optional[str]
    oauth_code: Optional[str]
    api_token: Optional[str]


class ChatPayload(BaseModel):
    session_id: str
    message: str
    metadata: Optional[dict] = None


@app.post("/auth/register")
def register(p: RegisterPayload):
    user = register_user(p.email, p.password)
    return {"user_id": user.user_id}


@app.post("/auth/login")
def login(p: LoginPayload):
    user = None
    if p.api_token:
        user = authenticate_api_token(p.api_token)
    elif p.oauth_provider and p.oauth_code:
        user = oauth_fallback(p.oauth_provider, p.oauth_code)
    elif p.email and p.password:
        user = authenticate_email_password(p.email, p.password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_jwt({"user_id": user.user_id, "role": user.role, "scopes": user.scopes})
    return {"token": token, "user_id": user.user_id, "role": user.role, "scopes": user.scopes}


@app.post("/session/init")
async def session_init(request: Request):
    await request.json()
    token = request.headers.get("Authorization") or ""
    if token.startswith("Bearer "):
        token = token[7:]
    payload = verify_jwt(token) if token else None
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    user = User(
        user_id=payload.get("user_id"), role=payload.get("role"), scopes=payload.get("scopes", [])
    )
    s = init_session(user)
    write_session(s.session_id, s.dict())
    log_event({"user_id": user.user_id, "action": "session_init", "session_id": s.session_id})
    return s.dict()


@app.post("/chat/process")
def chat_process(p: ChatPayload, authorization: Optional[str] = Header(None)):
    token = authorization or ""
    if token.startswith("Bearer "):
        token = token[7:]
    payload = verify_jwt(token) if token else None
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    session = read_session(p.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")

    # Delegate orchestration to the orchestrator module which handles routing,
    # agent invocation, verification, retries and escalation.
    result = orchestrate_input(
        user_id=payload.get("user_id"), session_id=p.session_id, user_input=p.message
    )
    if result.get("status") in ("failed", "escalated"):
        raise HTTPException(status_code=500, detail=result)
    return result


@app.post("/webhook/stripe")
async def webhook_stripe(request: Request, stripe_signature: Optional[str] = Header(None)):
    # In production verify signature with Stripe SDK
    event = await request.json()
    # Example: update user role on successful checkout
    # TODO: implement lookup and role update
    log_event({"action": "stripe_webhook_received", "event": str(event)})
    return {"status": "ok"}
