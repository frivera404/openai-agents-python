import asyncio
import logging

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent


logger = logging.getLogger(__name__)


async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            # Keep streaming deltas printed to stdout for interactive display.
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
