import asyncio
import shutil

import logging

from agents import Agent, Runner, trace
from agents.mcp import MCPServer, MCPServerStdio

logger = logging.getLogger(__name__)


async def run(mcp_server: MCPServer, directory_path: str):
    agent = Agent(
        name="Assistant",
        instructions=f"Answer questions about the git repository at {directory_path}, use that for repo_path",
        mcp_servers=[mcp_server],
    )

    message = "Who's the most frequent contributor?"
    logger.info("\n" + "-" * 40)
    logger.info(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    logger.info(result.final_output)

    message = "Summarize the last change in the repository."
    logger.info("\n" + "-" * 40)
    logger.info(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    logger.info(result.final_output)


async def main():
    # Ask the user for the directory path
    directory_path = input("Please enter the path to the git repository: ")

    async with MCPServerStdio(
        cache_tools_list=True,  # Cache the tools list, for demonstration
        params={"command": "uvx", "args": ["mcp-server-git"]},
    ) as server:
        with trace(workflow_name="MCP Git Example"):
            await run(server, directory_path)


if __name__ == "__main__":
    if not shutil.which("uvx"):
        raise RuntimeError("uvx is not installed. Please install it with `pip install uvx`.")
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)

    asyncio.run(main())
