"""
Example demonstrating Redis session memory functionality.

This example shows how to use Redis-backed session memory to maintain conversation
history across multiple agent runs with persistence and scalability.

Note: This example clears the session at the start to ensure a clean demonstration.
In production, you may want to preserve existing conversation history.
"""

import asyncio
import logging

from agents import Agent, Runner
from agents.extensions.memory import RedisSession


async def main():
    # Create an agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
    )

    logger = logging.getLogger(__name__)
    logger.info("=== Redis Session Example ===")
    logger.info("This example requires Redis to be running on localhost:6379")
    logger.info("Start Redis with: redis-server")
    logger.info("")

    # Create a Redis session instance
    session_id = "redis_conversation_123"
    try:
        session = RedisSession.from_url(
            session_id,
            url="redis://localhost:6379/0",  # Use database 0
        )

        # Test Redis connectivity
        if not await session.ping():
            logger = logging.getLogger(__name__)
            logger.error("Redis server is not available!")
            logger.error("Please start Redis server and try again.")
            return

        logger = logging.getLogger(__name__)
        logger.info("Connected to Redis successfully!")
        logger.info(f"Session ID: {session_id}")

        # Clear any existing session data for a clean start
        await session.clear_session()
        logger.info("Session cleared for clean demonstration.")
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
        logger.info("Redis session automatically handles conversation history with persistence.")

        # Demonstrate session persistence
        logger.info("\n=== Session Persistence Demo ===")
        all_items = await session.get_items()
        logger.info(f"Total messages stored in Redis: {len(all_items)}")

        # Demonstrate the limit parameter
        logger.info("\n=== Latest Items Demo ===")
        latest_items = await session.get_items(limit=2)
        logger.info("Latest 2 items:")
        for i, msg in enumerate(latest_items, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            logger.info(f"  {i}. {role}: {content}")

        # Demonstrate session isolation with a new session
        logger.info("\n=== Session Isolation Demo ===")
        new_session = RedisSession.from_url(
            "different_conversation_456",
            url="redis://localhost:6379/0",
        )

        logger.info("Creating a new session with different ID...")
        result = await Runner.run(
            agent,
            "Hello, this is a new conversation!",
            session=new_session,
        )
        logger.info(f"New session response: {result.final_output}")

        # Show that sessions are isolated
        original_items = await session.get_items()
        new_items = await new_session.get_items()
        logger.info(f"Original session has {len(original_items)} items")
        logger.info(f"New session has {len(new_items)} items")
        logger.info("Sessions are completely isolated!")

        # Clean up the new session
        await new_session.clear_session()
        await new_session.close()

        # Optional: Demonstrate TTL (time-to-live) functionality
        logger.info("\n=== TTL Demo ===")
        ttl_session = RedisSession.from_url(
            "ttl_demo_session",
            url="redis://localhost:6379/0",
            ttl=3600,  # 1 hour TTL
        )

        await Runner.run(
            agent,
            "This message will expire in 1 hour",
            session=ttl_session,
        )
        logger.info("Created session with 1-hour TTL - messages will auto-expire")

        await ttl_session.close()

        # Close the main session
        await session.close()

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception("Error: %s", e)
        logger.error("Make sure Redis is running on localhost:6379")


async def demonstrate_advanced_features():
    """Demonstrate advanced Redis session features."""
    logger = logging.getLogger(__name__)
    logger.info("\n=== Advanced Features Demo ===")

    # Custom key prefix for multi-tenancy
    tenant_session = RedisSession.from_url(
        "user_123",
        url="redis://localhost:6379/0",
        key_prefix="tenant_abc:sessions",  # Custom prefix for isolation
    )

    try:
        if await tenant_session.ping():
            logger.info("Custom key prefix demo:")
            await Runner.run(
                Agent(name="Support", instructions="Be helpful"),
                "Hello from tenant ABC",
                session=tenant_session,
            )
            logger.info("Session with custom key prefix created successfully")

        await tenant_session.close()
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception("Advanced features error: %s", e)


if __name__ == "__main__":
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)

    asyncio.run(main())
    asyncio.run(demonstrate_advanced_features())
