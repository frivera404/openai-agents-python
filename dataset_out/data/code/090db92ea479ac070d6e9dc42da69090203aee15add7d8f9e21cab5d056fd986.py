"""Standalone orchestrator app: single script exposing /orchestrate and Stripe webhook.

This bundles the orchestrator and webhook gating into one FastAPI app for easy
deployment/testing. It relies on `workflows.agent_system.orchestrator` and
`workflows.agent_system.auth` for orchestration and auth updates.
"""

import json
import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from .auth import update_user_role, verify_jwt
from .logger import log_event
from .orchestrator import orchestrate_input

app = FastAPI(title="Orchestrator App")


class OrchestratePayload(BaseModel):
    session_id: str
    message: str


@app.post("/orchestrate")
async def orchestrate_endpoint(p: OrchestratePayload, authorization: Optional[str] = Header(None)):
    token = authorization or ""
    if token.startswith("Bearer "):
        token = token[7:]
    payload = verify_jwt(token) if token else None
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")

    user_id = payload.get("user_id")
    result = orchestrate_input(user_id=user_id, session_id=p.session_id, user_input=p.message)
    if result.get("status") in ("failed", "escalated"):
        raise HTTPException(status_code=500, detail=result)
    return result


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """Handle Stripe webhooks and gate paid access.

    Expected behavior: for a successful checkout or invoice payment, update the
    corresponding user's role to `paid` and grant payment-related scopes. The
    Stripe Checkout session or invoice should include `metadata.user_id`.
    """
    payload = await request.body()
    sig = stripe_signature
    endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

    event = None
    # Try to verify signature if stripe library is available and secret set
    try:
        import stripe

        if endpoint_secret and sig:
            event = stripe.Webhook.construct_event(payload, sig, endpoint_secret)
        else:
            event = json.loads(payload.decode())
    except Exception:
        try:
            event = json.loads(payload.decode())
        except Exception as err:
            log_event({"action": "stripe_webhook_invalid", "error": "invalid payload"})
            raise HTTPException(status_code=400, detail="invalid payload") from err

    # Process event types
    etype = event.get("type")
    data = event.get("data", {}).get("object", {})
    metadata = data.get("metadata", {}) if isinstance(data, dict) else {}
    user_id = metadata.get("user_id")

    log_event({"action": "stripe_event_received", "type": etype, "user_id": user_id})

    if etype in (
        "checkout.session.completed",
        "invoice.payment_succeeded",
        "payment_intent.succeeded",
    ):
        if user_id:
            update_user_role(user_id, "paid", scopes=["chat", "domains", "email", "payments"])
            log_event({"action": "user_upgraded", "user_id": user_id})
            return {"status": "ok"}
        else:
            log_event({"action": "stripe_event_missing_user", "type": etype})
            return {"status": "ok", "warning": "no user_id metadata"}

    # For other events just acknowledge
    return {"status": "ignored", "type": etype}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8081")))
