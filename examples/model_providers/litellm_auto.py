from __future__ import annotations

import asyncio

from agents import Agent, ModelSettings, Runner, function_tool, set_tracing_disabled
import logging
from pydantic import BaseModel

"""This example uses the built-in support for LiteLLM. To use this, ensure you have the
OPENAI_API_KEY environment variable set.
"""

set_tracing_disabled(disabled=True)

# import logging
# logging.basicConfig(level=logging.DEBUG)


@function_tool
def get_weather(city: str):
    logger = logging.getLogger(__name__)
    logger.debug("[debug] getting weather for %s", city)
    return f"The weather in {city} is sunny."


class Result(BaseModel):
    output_text: str
    tool_results: list[str]


async def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        # We prefix with litellm/ to tell the Runner to use the LitellmModel
        model="litellm/openai/gpt-4o",
        tools=[get_weather],
        model_settings=ModelSettings(tool_choice="required"),
        output_type=Result,
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    logging.getLogger(__name__).info(result.final_output)


if __name__ == "__main__":
    import os

    if os.getenv("OPENAI_API_KEY") is None:
        raise ValueError(
            "OPENAI_API_KEY is not set. Please set it the environment variable and try again."
        )

    asyncio.run(main())
