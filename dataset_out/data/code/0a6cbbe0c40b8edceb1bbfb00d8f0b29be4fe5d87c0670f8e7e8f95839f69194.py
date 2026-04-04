"""Connect to configured MCP servers and print tool lists.

Usage:
    uv run python scripts/connect_mcp_with_session.py

This will attempt to connect to each enabled MCP server from
`openai_assistant_config.json` and print initialization results
and available tools. It will add a `Session-Id` header with the
provided session id to HTTP-based servers to attempt session binding.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
import site
import sys

# Ensure venv site-packages is on sys.path when running via the venv python
repo_root = Path(__file__).resolve().parents[1]
venv_site = repo_root / ".venv" / "Lib" / "site-packages"
if venv_site.exists():
    site.addsitedir(str(venv_site))
    # Also ensure it's at front of sys.path for imports
    sys.path.insert(0, str(venv_site))
else:
    # Also try lower-case path on some systems
    venv_site_alt = repo_root / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if venv_site_alt.exists():
        site.addsitedir(str(venv_site_alt))
        sys.path.insert(0, str(venv_site_alt))


SESSION_ID = "fb5162eb1b534e7295866954a9f474d3"


async def connect_server(name: str, cfg: dict[str, Any]) -> None:
    from agents.mcp.server import MCPServerStdio, MCPServerStreamableHttp, MCPServerSse

    print(f"--- Connecting to {name} ({cfg.get('type', 'stdio')}) ---")
    server = None
    try:
        t = cfg.get("type", "stdio")
        if t == "stdio":
            params = {
                "command": cfg["command"],
                "args": cfg.get("args", []),
                "env": cfg.get("env", None),
                "cwd": cfg.get("cwd", None),
            }
            server = MCPServerStdio(params=params, client_session_timeout_seconds=30)

        else:
            # Use streamable HTTP transport for HTTP-like servers
            params: dict[str, Any] = {"url": cfg.get("url")}
            headers = cfg.get("headers") or {}
            # Add session id header if not already present
            headers.setdefault("Session-Id", SESSION_ID)
            params["headers"] = headers
            if cfg.get("timeout") is not None:
                params["timeout"] = cfg.get("timeout")
            if cfg.get("sse_read_timeout") is not None:
                params["sse_read_timeout"] = cfg.get("sse_read_timeout")

            # Prefer streamable HTTP where possible
            server = MCPServerStreamableHttp(params=params, client_session_timeout_seconds=30)

        await server.connect()

        init = getattr(server, "server_initialize_result", None)
        print(f"{name} initialized: {init}")

        try:
            tools = await server.list_tools()
            print(f"{name} tools: {[t.name for t in tools]}")
        except Exception as e:  # noqa: BLE001 - report errors
            print(f"{name} list_tools failed: {e}")

    except Exception as e:
        print(f"{name} connection failed: {e}")
    finally:
        if server is not None:
            try:
                await server.cleanup()
            except Exception:
                pass


async def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    cfg_path = repo_root / "openai_assistant_config.json"
    if not cfg_path.exists():
        print(f"Config file not found: {cfg_path}")
        return

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    servers = cfg.get("mcp_servers", {})
    tasks = []
    for name, s in servers.items():
        if not s.get("enabled", True):
            print(f"Skipping disabled server {name}")
            continue
        tasks.append(connect_server(name, s))

    if not tasks:
        print("No enabled MCP servers found in config")
        return

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
