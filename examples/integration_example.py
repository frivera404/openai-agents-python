import asyncio
import os
import logging
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server):
    agent = Agent(
        name="Assistant",
        instructions="Use the filesystem tools to answer questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # List directory
    message = "List the contents of the root directory."
    logger = logging.getLogger(__name__)
    logger.info("Running: %s", message)
    result = await Runner.run(starting_agent=agent, input=message)
    logger.info(result.final_output)


async def main():
    async with MCPServerStreamableHttp(
        name="Docker Filesystem Server",
        params={
            "url": "http://mcp-filesystem:8000/mcp",
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Docker Filesystem Integration", trace_id=trace_id):
            logging.getLogger(__name__).info(
                "View trace: https://platform.openai.com/traces/trace?trace_id=%s\n", trace_id
            )
            await run(server)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())