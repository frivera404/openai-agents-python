#!/usr/bin/env python3
"""
Integration example that connects an Agent to the Docker MCP filesystem server.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

# Ensure the repository's `src` directory is on the Python path so `agents` can be imported.
for parent in Path(__file__).resolve().parents:
    candidate = parent / "src"
    if candidate.is_dir():
        sys.path.insert(0, str(candidate))
        break

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

DEFAULT_PROMPT: Final[str] = (
    "List the files you can read, then read any README.md you find and summarise it."
)
PROMPT: Final[str] = os.environ.get("FILESYSTEM_MCP_PROMPT", DEFAULT_PROMPT)
FILESYSTEM_MCP_URL: Final[str] = os.environ.get(
    "FILESYSTEM_MCP_URL", "http://mcp-filesystem:8000/mcp"
)


async def main() -> None:
    """Run a simple agent that exercises the filesystem MCP server."""
    logger.info("Connecting to MCP server at %s", FILESYSTEM_MCP_URL)

    async with MCPServerStreamableHttp(
        name="docker-mcp-filesystem",
        params={"url": FILESYSTEM_MCP_URL},
        cache_tools_list=True,
    ) as server:
        agent = Agent(
            name="Filesystem Inspector",
            instructions=(
                "You have access to filesystem tools. "
                "Use them to inspect files and answer questions."
            ),
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required"),
        )

        trace_id = gen_trace_id()
        with trace(workflow_name="Filesystem MCP Integration", trace_id=trace_id):
            logger.info("Run trace: https://platform.openai.com/traces/trace?trace_id=%s", trace_id)
            result = await Runner.run(starting_agent=agent, input=PROMPT)
            logger.info("Agent output:\n")
            logger.info("%s", result.final_output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
