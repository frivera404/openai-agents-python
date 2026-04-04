from typing import Optional

import requests


class HTTPTool:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch(self, url: str, params: Optional[dict] = None) -> dict:
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            # Return minimal response for workers
            return {"status_code": r.status_code, "text": r.text[:5000]}
        except Exception as e:
            return {"error": str(e)}

    def post(self, url: str, json: dict, timeout: Optional[int] = None) -> dict:
        try:
            r = requests.post(url, json=json, timeout=timeout or self.timeout)
            r.raise_for_status()
            return {
                "status_code": r.status_code,
                "json": r.json()
                if r.headers.get("content-type", "").startswith("application/json")
                else None,
            }
        except Exception as e:
            return {"error": str(e)}
