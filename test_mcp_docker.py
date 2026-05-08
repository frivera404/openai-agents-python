#!/usr/bin/env python3
"""
Test MCP Integration with Docker Services
"""

import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp


async def main():
    # MCP server for filesystem access
    mcp_server = MCPServerStreamableHttp(
        name="Docker Filesystem Server",
        params={
            "url": "http://mcp-filesystem:8000/mcp",
        },
    )

    # Agent setup
    agent = Agent(
        name="Test Agent",
        instructions="You are a helpful assistant that can use filesystem tools.",
        mcp_servers=[mcp_server],
    )

    # Test task
    result = await Runner.run(starting_agent=agent, input="List the contents of the root directory.")
    print("Agent response:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())