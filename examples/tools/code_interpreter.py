import asyncio
import logging

from agents import Agent, CodeInterpreterTool, Runner, trace


async def main():
    agent = Agent(
        name="Code interpreter",
        # Note that using gpt-5 model with streaming for this tool requires org verification
        # Also, code interpreter tool does not support gpt-5's minimal reasoning effort
        model="gpt-4.1",
        instructions="You love doing math.",
        tools=[
            CodeInterpreterTool(
                tool_config={"type": "code_interpreter", "container": {"type": "auto"}},
            )
        ],
    )

    with trace("Code interpreter example"):
        logger = logging.getLogger(__name__)
        logger.info("Solving math problem...")
        result = Runner.run_streamed(agent, "What is the square root of273 * 312821 plus 1782?")
        async for event in result.stream_events():
            if (
                event.type == "run_item_stream_event"
                and event.item.type == "tool_call_item"
                and event.item.raw_item.type == "code_interpreter_call"
            ):
                logger.info("Code interpreter code:\n```\n%s\n```\n", event.item.raw_item.code)
            elif event.type == "run_item_stream_event":
                logger.info("Other event: %s", event.item.type)

            logger.info("Final output: %s", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
