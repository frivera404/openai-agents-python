from agent_private_i.workers.base import WorkerBase
import os


class ResearchBotWorker(WorkerBase):
    role = "research_bot"

    def run(self, step: dict, task_payload: dict) -> dict:
        # Try to use MCPTool if configured, else HTTPTool if a URL is provided, else fallback.
        query = task_payload.get("inputs", {}).get("query") or task_payload.get("goal")
        # Lazy imports to avoid hard dependency if not needed
        mcp_base = os.environ.get("MCP_BASE_URL")
        if mcp_base:
            try:
                from agent_private_i.tools.mcp_tool import MCPTool

                m = MCPTool(mcp_base)
                resp = m.search_files(path=".", query=query, max_results=5)
                return {"notes": f"MCP search returned", "mcp": resp}
            except Exception as e:
                return {"error": f"MCP search failed: {e}"}

        # fallback: try HTTP fetch to a provided url in inputs
        url = task_payload.get("inputs", {}).get("url")
        if url:
            try:
                from agent_private_i.tools.http_tool import HTTPTool

                http = HTTPTool()
                r = http.fetch(url, params={"q": query})
                return {"notes": "HTTP fetch done", "http": r}
            except Exception as e:
                return {"error": f"HTTP fetch failed: {e}"}

        # final fallback: local placeholder
        notes = f"Researched (placeholder): '{query}'."
        return {"notes": notes}
