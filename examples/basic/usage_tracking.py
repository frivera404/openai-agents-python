import asyncio
import logging

from agents import Agent, Runner, Usage, function_tool
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    """Get the current weather information for a specified city."""
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")


def print_usage(usage: Usage) -> None:
    logger.info("=== Usage ===")
    logger.info("Requests: %s", usage.requests)
    logger.info("Input tokens: %s", usage.input_tokens)
    logger.info("Output tokens: %s", usage.output_tokens)
    logger.info("Total tokens: %s", usage.total_tokens)


async def main() -> None:
    agent = Agent(
        name="Usage Demo",
        instructions="You are a concise assistant. Use tools if needed.",
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")

    logger.info("Final output:")
    logger.info("%s", result.final_output)

    # Access usage from the run context
    print_usage(result.context_wrapper.usage)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
