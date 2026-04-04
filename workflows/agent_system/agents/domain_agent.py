from typing import Any


class DomainAgent:
    """Handles domain operations (GoDaddy API wrapper in production)."""

    def __init__(self, tools_registry=None):
        self.tools = tools_registry

    def handle(self, payload: dict[str, Any]) -> dict:
        # payload: {"action": "buy", "domain": "example.com", ...}
        domain = payload.get("domain")
        if not domain:
            return {"status": "error", "reason": "missing domain"}
        # In production call GoDaddy REST tool here.
        return {
            "status": "success",
            "action": "buy_domain",
            "domain": domain,
            "checkout": f"https://godaddy.example/checkout?d={domain}",
        }
