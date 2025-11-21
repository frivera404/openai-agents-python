import asyncio
import logging

from agents import Agent, Runner, WebSearchTool, trace

logger = logging.getLogger(__name__)


async def main():
    agent = Agent(
        name="Web searcher",
        instructions="You are a helpful agent.",
        tools=[WebSearchTool(user_location={"type": "approximate", "city": "New York"})],
    )

    with trace("Web search example"):
        result = await Runner.run(
            agent,
            "search the web for 'local sports news' and give me 1 interesting update in a sentence.",
        )
        logger.info("%s", result.final_output)
        # The New York Giants are reportedly pursuing quarterback Aaron Rodgers after his ...


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
