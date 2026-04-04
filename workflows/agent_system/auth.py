"""Simple auth utilities: JWT-like tokens and session init.

This is a scaffold for the required flows: email/password, OAuth placeholder,
and API token authentication. Secrets must be provided via env vars.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

from .models import Session, User

JWT_SECRET = os.environ.get("AGENTS_JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = int(os.environ.get("AGENTS_JWT_EXP", "3600"))


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64ud(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding and padding != 4:
        s = s + ("=" * padding)
    return base64.urlsafe_b64decode(s.encode())


def create_jwt(payload: dict) -> str:
    header = {"alg": JWT_ALGO, "typ": "JWT"}
    payload = dict(payload)
    payload.setdefault("exp", int(time.time()) + JWT_EXP_SECONDS)
    header_b = _b64u(json.dumps(header, separators=(",", ":")).encode())
    payload_b = _b64u(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b}.{payload_b}".encode()
    sig = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    sig_b = _b64u(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def verify_jwt(token: str) -> dict | None:
    try:
        header_b, payload_b, sig_b = token.split(".")
        signing_input = f"{header_b}.{payload_b}".encode()
        expected = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64ud(sig_b)):
            return None
        payload = json.loads(_b64ud(payload_b))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


# --- Authentication flows (stubs) ---
_USER_DB: dict[str, User] = {}


def register_user(email: str, password: str, role: str = "free", scopes=None) -> User:
    # In production, use a proper user DB and secure password hashing.
    scopes = scopes or ["chat"]
    user = User(email=email, role=role, scopes=scopes)
    _USER_DB[email] = {"user": user, "password": password}
    return user


def authenticate_email_password(email: str, password: str) -> User | None:
    rec = _USER_DB.get(email)
    if rec and rec.get("password") == password:
        return rec["user"]
    return None


def authenticate_api_token(token: str) -> User | None:
    # Implement mapping from token->user in production.
    # For scaffold, accept token=="automation-token" as admin.
    if token == "automation-token":
        return User(
            email="automation@local", role="admin", scopes=["chat", "domains", "email", "payments"]
        )
    return None


def oauth_fallback(provider: str, code: str) -> User | None:
    # Placeholder: exchange code for user info with provider.
    return User(email=f"{provider}_user@example.com", role="free", scopes=["chat"])


def init_session(user: User, memory_scope: str = "private") -> Session:
    s = Session(user_id=user.user_id, memory_scope=memory_scope)
    return s


def update_user_role(user_id: str, role: str, scopes: list | None = None) -> User | None:
    """Update a user's role and scopes by user_id in the simple user store.

    Returns the updated User or None if not found.
    """
    for rec in _USER_DB.values():
        u = rec.get("user")
        if u and u.user_id == user_id:
            u.role = role
            if scopes is not None:
                u.scopes = scopes
            return u
    return None
