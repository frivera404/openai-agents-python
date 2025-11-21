"""
Example demonstrating encrypted session memory functionality.

This example shows how to use encrypted session memory to maintain conversation history
across multiple agent runs with automatic encryption and TTL-based expiration.
The EncryptedSession wrapper provides transparent encryption over any underlying session.
"""

import asyncio
import logging
from typing import cast

from agents import Agent, Runner, SQLiteSession
from agents.extensions.memory import EncryptedSession
from agents.extensions.memory.encrypt_session import EncryptedEnvelope


logger = logging.getLogger(__name__)


async def main():
    # Create an agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
    )

    # Create an underlying session (SQLiteSession in this example)
    session_id = "conversation_123"
    underlying_session = SQLiteSession(session_id)

    # Wrap with encrypted session for automatic encryption and TTL
    session = EncryptedSession(
        session_id=session_id,
        underlying_session=underlying_session,
        encryption_key="my-secret-encryption-key",
        ttl=3600,  # 1 hour TTL for messages
    )

    logger.info("=== Encrypted Session Example ===")
    logger.info("The agent will remember previous messages automatically with encryption.\n")

    # First turn
    logger.info("First turn:")
    logger.info("User: What city is the Golden Gate Bridge in?")
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session,
    )
    logger.info("Assistant: %s", result.final_output)
    logger.info("")

    # Second turn - the agent will remember the previous conversation
    logger.info("Second turn:")
    logger.info("User: What state is it in?")
    result = await Runner.run(agent, "What state is it in?", session=session)
    logger.info("Assistant: %s", result.final_output)
    logger.info("")

    # Third turn - continuing the conversation
    logger.info("Third turn:")
    logger.info("User: What's the population of that state?")
    result = await Runner.run(
        agent,
        "What's the population of that state?",
        session=session,
    )
    logger.info("Assistant: %s", result.final_output)
    logger.info("")

    logger.info("=== Conversation Complete ===")
    logger.info("Notice how the agent remembered the context from previous turns!")
    logger.info("All conversation history was automatically encrypted and stored securely.")

    # Demonstrate the limit parameter - get only the latest 2 items
    logger.info("\n=== Latest Items Demo ===")
    latest_items = await session.get_items(limit=2)
    logger.info("Latest 2 items (automatically decrypted):")
    for i, msg in enumerate(latest_items, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        logger.info("  %d. %s: %s", i, role, content)

    logger.info("\nFetched %s out of total conversation history.", len(latest_items))

    # Get all items to show the difference
    all_items = await session.get_items()
    logger.info("Total items in session: %s", len(all_items))

    # Show that underlying storage is encrypted
    logger.info("\n=== Encryption Demo ===")
    logger.info("Checking underlying storage to verify encryption...")
    raw_items = await underlying_session.get_items()
    logger.info("Raw encrypted items in underlying storage:")
    for i, item in enumerate(raw_items, 1):
        if isinstance(item, dict) and item.get("__enc__") == 1:
            enc_item = cast(EncryptedEnvelope, item)
            logger.info(
                "  %d. Encrypted envelope: __enc__=%s, payload length=%d",
                i,
                enc_item["__enc__"],
                len(enc_item["payload"]),
            )
        else:
            logger.info("  %d. Unencrypted item: %s", i, item)

    logger.info("\nAll %s items are stored encrypted with TTL-based expiration.", len(raw_items))

    # Clean up
    underlying_session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
