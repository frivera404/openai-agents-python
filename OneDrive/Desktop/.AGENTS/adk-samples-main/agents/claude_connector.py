import os
import requests
from typing import Any, Dict, Optional


class ClaudeConnector:
    """Minimal Claude/Anthropic HTTP client wrapper.

    Reads `CLAUDE_API_KEY` and optional `CLAUDE_API_URL` from the environment
    by default. Call `generate()` to get a JSON response from the API.
    """

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, timeout: int = 60):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not set in environment or constructor")

        self.api_url = api_url or os.getenv("CLAUDE_API_URL", "https://api.anthropic.com/v1/complete")
        self.timeout = timeout

    def generate(self, prompt: str, model: str = "claude-2.1", max_tokens: int = 300, temperature: float = 0.0) -> Dict[str, Any]:
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
