"""
Example demonstrating session memory functionality.

This example shows how to use session memory to maintain conversation history
across multiple agent runs without manually handling .to_input_list().
"""

import asyncio
import logging

from agents import Agent, Runner, SQLiteSession


async def main():
    # Create an agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
    )

    # Create a session instance that will persist across runs
    session_id = "conversation_123"
    session = SQLiteSession(session_id)

    logger = logging.getLogger(__name__)
    logger.info("=== Session Example ===")
    logger.info("The agent will remember previous messages automatically.\n")

    # First turn
    logger.info("First turn:")
    logger.info("User: What city is the Golden Gate Bridge in?")
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    logger.info("")

    # Second turn - the agent will remember the previous conversation
    logger.info("Second turn:")
    logger.info("User: What state is it in?")
    result = await Runner.run(agent, "What state is it in?", session=session)
    logger.info(f"Assistant: {result.final_output}")
    logger.info("")

    # Third turn - continuing the conversation
    logger.info("Third turn:")
    logger.info("User: What's the population of that state?")
    result = await Runner.run(
        agent,
        "What's the population of that state?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    logger.info("")

    logger.info("=== Conversation Complete ===")
    logger.info("Notice how the agent remembered the context from previous turns!")
    logger.info("Sessions automatically handles conversation history.")

    # Demonstrate the limit parameter - get only the latest 2 items
    logger.info("\n=== Latest Items Demo ===")
    latest_items = await session.get_items(limit=2)
    logger.info("Latest 2 items:")
    for i, msg in enumerate(latest_items, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        logger.info(f"  {i}. {role}: {content}")

    logger.info(f"\nFetched {len(latest_items)} out of total conversation history.")

    # Get all items to show the difference
    all_items = await session.get_items()
    logger.info(f"Total items in session: {len(all_items)}")


if __name__ == "__main__":
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)

    asyncio.run(main())
