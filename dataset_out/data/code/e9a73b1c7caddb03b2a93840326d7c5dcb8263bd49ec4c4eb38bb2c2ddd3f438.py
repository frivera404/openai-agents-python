from typing import Any


class PaymentAgent:
    """Handles Stripe checkout and subscription verification."""

    def __init__(self, tools_registry=None):
        self.tools = tools_registry

    def handle(self, payload: dict[str, Any]) -> dict:
        price_id = payload.get("price_id")
        user_id = payload.get("user_id")
        if not price_id or not user_id:
            return {"status": "error", "reason": "missing price_id or user_id"}
        # Call create_stripe_checkout tool
        return {
            "status": "success",
            "checkout_url": f"https://stripe.example/checkout?price={price_id}&user={user_id}",
        }
