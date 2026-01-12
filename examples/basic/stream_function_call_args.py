"""Streamed function call arguments example (cleaned stub).

This example is a simplified, lint-clean version of the original demo.
It demonstrates how function-call argument deltas might be streamed and
logged. Restore the original file from history if the full demo is
needed.
"""

import asyncio
import logging

from agents import Agent, Runner, function_tool

logger = logging.getLogger(__name__)


@function_tool
def write_file(filename: str, content: str) -> str:
    """Pretend to write a file and return a description string."""
    return f"File {filename} written (size={len(content)} bytes)"


async def simulate_streamed_function_call_args() -> None:
    """Async generator that simulates streaming deltas for function call args.

    Yields dict events with keys: `type`, `arg`, `chunk`, `final`.
    This mirrors how a model might stream incremental argument text.
    """

    # Stream filename in two chunks
    yield {"type": "function_call_arg_delta", "arg": "filename", "chunk": "report_", "final": False}
    await asyncio.sleep(0)
    yield {"type": "function_call_arg_delta", "arg": "filename", "chunk": "2024.txt", "final": True}
    await asyncio.sleep(0)

    # Stream file content in several small chunks
    content_chunks = [
        "This is the first line.\n",
        "Second line here.\n",
        "Final short note.\n",
    ]
    for i, c in enumerate(content_chunks):
        yield {"type": "function_call_arg_delta", "arg": "content", "chunk": c, "final": i == len(content_chunks) - 1}
        await asyncio.sleep(0)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Streamed function-call example (simulated)")

    # Assemble streamed args
    assembled: dict[str, str] = {"filename": "", "content": ""}
    finished = {"filename": False, "content": False}

    async for event in simulate_streamed_function_call_args():
        if event.get("type") != "function_call_arg_delta":
            continue
        arg = event["arg"]
        assembled[arg] += event["chunk"]
        if event.get("final"):
            finished[arg] = True

        # When all args are final, invoke the tool
        if all(finished.values()):
            res = write_file(assembled["filename"], assembled["content"])
            logger.info("Tool result: %s", res)
            break


if __name__ == "__main__":
    asyncio.run(main())
