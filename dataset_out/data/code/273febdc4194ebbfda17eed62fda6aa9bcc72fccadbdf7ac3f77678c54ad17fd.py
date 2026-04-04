from typing import Any, Callable


class ToolSpec:
    def __init__(
        self, name: str, func: Callable, input_schema: dict = None, output_schema: dict = None
    ):
        self.name = name
        self.func = func
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}


class ToolsRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec):
        self._tools[spec.name] = spec

    def call(self, name: str, payload: dict[str, Any]):
        spec = self._tools.get(name)
        if not spec:
            raise KeyError(f"tool not found: {name}")
        return spec.func(payload)


# Example tool implementations (stubs)
def create_stripe_checkout(payload):
    return {
        "checkout_url": f"https://stripe.example/checkout?price={payload.get('price_id')}",
        "status": "success",
    }


def send_email_tool(payload):
    return {"status": "sent", "to": payload.get("to")}


def make_default_registry():
    r = ToolsRegistry()
    r.register(
        ToolSpec(
            "create_stripe_checkout",
            create_stripe_checkout,
            {"price_id": "string", "user_id": "string"},
            {"checkout_url": "string"},
        )
    )
    r.register(
        ToolSpec(
            "send_email",
            send_email_tool,
            {"to": "string", "subject": "string", "body": "string"},
            {"status": "string"},
        )
    )
    return r
