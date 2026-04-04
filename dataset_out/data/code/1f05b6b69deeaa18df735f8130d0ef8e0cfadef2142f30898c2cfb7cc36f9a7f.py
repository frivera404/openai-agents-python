"""Supervisor / Router agent: classify intent, enforce permissions, route."""


from .models import IntentRoute, Session


def classify_intent(message: str) -> dict:
    m = message.lower()
    if "buy" in m and "domain" in m:
        return {"intent": "buy_domain", "confidence": 0.95}
    if "send" in m and "email" in m:
        return {"intent": "send_email", "confidence": 0.9}
    if "checkout" in m or "subscribe" in m or "pay" in m:
        return {"intent": "checkout", "confidence": 0.92}
    return {"intent": "content", "confidence": 0.7}


def route_intent(intent: str, session: Session, user_scopes: list) -> IntentRoute:
    # Enforce scopes and route
    if intent == "buy_domain":
        if "domains" not in user_scopes:
            return IntentRoute(route_to="VerifierAgent", confidence=0.0)
        return IntentRoute(route_to="DomainAgent", confidence=0.94)
    if intent == "send_email":
        if "email" not in user_scopes:
            return IntentRoute(route_to="VerifierAgent", confidence=0.0)
        return IntentRoute(route_to="EmailAgent", confidence=0.93)
    if intent == "checkout":
        if "payments" not in user_scopes:
            return IntentRoute(route_to="VerifierAgent", confidence=0.0)
        return IntentRoute(route_to="PaymentAgent", confidence=0.95)
    return IntentRoute(route_to="ContentAgent", confidence=0.8)
