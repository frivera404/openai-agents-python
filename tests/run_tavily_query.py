import asyncio
import json
import os
import sys

# Ensure project root is on sys.path so we can import mcp_client when running from tests/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mcp_client import MCPClientConfig, MCPClient


async def main():
    cfg = MCPClientConfig("mcp_config.json")
    client = MCPClient(cfg)

    ok = await client.initialize_servers(["tavily-remote-mcp"])
    if not ok:
        print("Failed to initialize tavily server")
        return

    try:
        for server in client.mcp_servers:
            print(f"Connected server: {server.name}")
            try:
                tools = await server.list_tools()
                print("Tools:", [t.name for t in tools])
                if any(t.name == "tavily_search" for t in tools):
                    print("Invoking tavily_search...")
                    result = await server.call_tool("tavily_search", {"query": "ctdatenight offers"})
                    # Try to extract structured_content or content
                    payload = getattr(result, "structured_content", None) or getattr(result, "content", None) or result
                    print(json.dumps(payload, ensure_ascii=False, default=str, indent=2)[:4000])
                    return
            except Exception as e:
                print(f"Error querying server {server.name}: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
