from typing import Any


class EmailAgent:
    """Handles transactional and campaign emails."""

    def __init__(self, tools_registry=None):
        self.tools = tools_registry

    def handle(self, payload: dict[str, Any]) -> dict:
        to = payload.get("to")
        subject = payload.get("subject", "No Subject")
        payload.get("body", "")
        if not to:
            return {"status": "error", "reason": "missing recipient"}
        # Call SMTP / SendGrid tool in production
        return {"status": "queued", "to": to, "subject": subject}
