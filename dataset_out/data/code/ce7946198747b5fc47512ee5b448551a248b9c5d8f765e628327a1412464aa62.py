import os
from typing import Optional

from .http_tool import HTTPTool


class MCPTool:
    def __init__(self, base_url: Optional[str] = None):
        # base_url can be like http://127.0.0.1:8000
        self.base_url = base_url or os.environ.get("MCP_BASE_URL")
        self.http = HTTPTool()

    def call(self, path: str, payload: dict) -> dict:
        if not self.base_url:
            return {"error": "No MCP base URL configured"}
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        return self.http.post(url, json=payload)

    def search_files(self, path: str, query: str, max_results: int = 10) -> dict:
        return self.call(
            "automation/filesystem/search",
            {"path": path, "query": query, "max_results": max_results},
        )
