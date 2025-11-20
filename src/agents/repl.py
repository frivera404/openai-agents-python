from __future__ import annotations

from typing import Any

from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent
from ..logger import logger

from .agent import Agent
from .items import TResponseInputItem
from .result import RunResultBase
from .run import Runner
from .run_context import TContext
from .stream_events import AgentUpdatedStreamEvent, RawResponsesStreamEvent, RunItemStreamEvent


async def run_demo_loop(
    agent: Agent[Any], *, stream: bool = True, context: TContext | None = None
) -> None:
    """Run a simple REPL loop with the given agent.

    This utility allows quick manual testing and debugging of an agent from the
    command line. Conversation state is preserved across turns. Enter ``exit``
    or ``quit`` to stop the loop.

    Args:
        agent: The starting agent to run.
        stream: Whether to stream the agent output.
        context: Additional context information to pass to the runner.
    """

    current_agent = agent
    input_items: list[TResponseInputItem] = []
    while True:
        try:
            user_input = input(" > ")
        except (EOFError, KeyboardInterrupt):
            logger.debug("REPL: received EOF/KeyboardInterrupt, exiting loop")
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        input_items.append({"role": "user", "content": user_input})

        result: RunResultBase
        if stream:
            result = Runner.run_streamed(current_agent, input=input_items, context=context)
            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        logger.debug(event.data.delta)
                elif isinstance(event, RunItemStreamEvent):
                    if event.item.type == "tool_call_item":
                        logger.debug("[tool called]")
                    elif event.item.type == "tool_call_output_item":
                        logger.debug(f"[tool output: {event.item.output}]")
                elif isinstance(event, AgentUpdatedStreamEvent):
                    logger.debug(f"[Agent updated: {event.new_agent.name}]")
            logger.debug("REPL: stream finished for turn")
        else:
            result = await Runner.run(current_agent, input_items, context=context)
            if result.final_output is not None:
                logger.debug("REPL final_output: %s", result.final_output)

        current_agent = result.last_agent
        input_items = result.to_input_list()
