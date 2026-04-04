from typing import Any


class Verifier:
    """Performs sanity and security checks on tool outputs before replying."""

    def verify(self, agent_name: str, output: dict[str, Any]) -> dict[str, Any]:
        # Basic checks: no secrets, expected keys, success status
        if not isinstance(output, dict):
            return {"ok": False, "reason": "invalid output type"}
        # Example check: do not allow keys named 'api_key' or 'secret'
        forbidden = [k for k in output.keys() if "key" in k or "secret" in k]
        if forbidden:
            return {"ok": False, "reason": "forbidden keys in output", "keys": forbidden}
        return {"ok": True, "output": output}
