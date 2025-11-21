"""
Comprehensive example demonstrating AdvancedSQLiteSession functionality.

This example shows both basic session memory features and advanced conversation
branching capabilities, including usage statistics, turn-based organization,
and multi-timeline conversation management.
"""

import asyncio
import logging

from agents import Agent, Runner, function_tool
from agents.extensions.memory import AdvancedSQLiteSession

logger = logging.getLogger(__name__)


@function_tool
async def get_weather(city: str) -> str:
    if city.strip().lower() == "new york":
        return f"The weather in {city} is cloudy."
    return f"The weather in {city} is sunny."


async def main():
    # Create an agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
        tools=[get_weather],
    )

    # Create an advanced session instance
    session = AdvancedSQLiteSession(
        session_id="conversation_comprehensive",
        create_tables=True,
    )

    logger.info("=== AdvancedSQLiteSession Comprehensive Example ===")
    logger.info("This example demonstrates both basic and advanced session features.\n")

    # === PART 1: Basic Session Functionality ===
    logger.info("=== PART 1: Basic Session Memory ===")
    logger.info("The agent will remember previous messages with structured tracking.\n")

    # First turn
    logger.info("First turn:")
    logger.info("User: What city is the Golden Gate Bridge in?")
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    logger.info(f"Usage: {result.context_wrapper.usage.total_tokens} tokens")

    # Store usage data automatically
    await session.store_run_usage(result)
    logger.info("")

    # Second turn - continuing the conversation
    logger.info("Second turn:")
    logger.info("User: What's the weather in that city?")
    result = await Runner.run(
        agent,
        "What's the weather in that city?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    logger.info(f"Usage: {result.context_wrapper.usage.total_tokens} tokens")

    # Store usage data automatically
    await session.store_run_usage(result)
    logger.info("")

    # Third turn
    logger.info("Third turn:")
    logger.info("User: What's the population of that city?")
    result = await Runner.run(
        agent,
        "What's the population of that city?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    logger.info(f"Usage: {result.context_wrapper.usage.total_tokens} tokens")

    # Store usage data automatically
    await session.store_run_usage(result)
    logger.info("")

    # === PART 2: Usage Tracking and Analytics ===
    logger.info("=== PART 2: Usage Tracking and Analytics ===")
    session_usage = await session.get_session_usage()
    if session_usage:
        logger.info("Session Usage (aggregated from turns):")
        logger.info(f"  Total requests: {session_usage['requests']}")
        logger.info(f"  Total tokens: {session_usage['total_tokens']}")
        logger.info(f"  Input tokens: {session_usage['input_tokens']}")
        logger.info(f"  Output tokens: {session_usage['output_tokens']}")
        logger.info(f"  Total turns: {session_usage['total_turns']}")

        # Show usage by turn
        turn_usage_list = await session.get_turn_usage()
        if turn_usage_list and isinstance(turn_usage_list, list):
            logger.info("\nUsage by turn:")
            for turn_data in turn_usage_list:
                turn_num = turn_data["user_turn_number"]
                tokens = turn_data["total_tokens"]
                logger.info(f"  Turn {turn_num}: {tokens} tokens")
    else:
        logger.info("No usage data found.")

    logger.info("\n=== Structured Query Demo ===")
    conversation_turns = await session.get_conversation_by_turns()
    logger.info("Conversation by turns:")
    for turn_num, items in conversation_turns.items():
        logger.info(f"  Turn {turn_num}: {len(items)} items")
        for item in items:
            if item["tool_name"]:
                logger.info(f"    - {item['type']} (tool: {item['tool_name']})")
            else:
                logger.info(f"    - {item['type']}")

    # Show tool usage
    tool_usage = await session.get_tool_usage()
    if tool_usage:
        logger.info("\nTool usage:")
        for tool_name, count, turn in tool_usage:
            logger.info(f"  {tool_name}: used {count} times in turn {turn}")
    else:
        logger.info("\nNo tool usage found.")

    logger.info("\n=== Original Conversation Complete ===")

    # Show current conversation
    logger.info("Current conversation:")
    current_items = await session.get_items()
    for i, item in enumerate(current_items, 1):
        role = str(item.get("role", item.get("type", "unknown")))
        if item.get("type") == "function_call":
            content = f"{item.get('name', 'unknown')}({item.get('arguments', '{}')})"
        elif item.get("type") == "function_call_output":
            content = str(item.get("output", ""))
        else:
            content = str(item.get("content", item.get("output", "")))
        logger.info(f"  {i}. {role}: {content}")

    logger.info(f"\nTotal items: {len(current_items)}")

    # === PART 3: Conversation Branching ===
    logger.info("\n=== PART 3: Conversation Branching ===")
    logger.info("Let's explore a different path from turn 2...")

    # Show available turns for branching
    logger.info("\nAvailable turns for branching:")
    turns = await session.get_conversation_turns()
    for turn in turns:
        logger.info(f"  Turn {turn['turn']}: {turn['content']}")

    # Create a branch from turn 2
    logger.info("\nCreating new branch from turn 2...")
    branch_id = await session.create_branch_from_turn(2)
    logger.info(f"Created branch: {branch_id}")

    # Show what's in the new branch (should have conversation up to turn 2)
    branch_items = await session.get_items()
    logger.info(f"Items copied to new branch: {len(branch_items)}")
    logger.info("New branch contains:")
    for i, item in enumerate(branch_items, 1):
        role = str(item.get("role", item.get("type", "unknown")))
        if item.get("type") == "function_call":
            content = f"{item.get('name', 'unknown')}({item.get('arguments', '{}')})"
        elif item.get("type") == "function_call_output":
            content = str(item.get("output", ""))
        else:
            content = str(item.get("content", item.get("output", "")))
        logger.info(f"  {i}. {role}: {content}")

    # Continue conversation in new branch
    logger.info("\nContinuing conversation in new branch...")
    logger.info("Turn 2 (new branch): User asks about New York instead")
    result = await Runner.run(
        agent,
        "Actually, what's the weather in New York instead?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    await session.store_run_usage(result)

    # Continue the new branch
    logger.info("Turn 3 (new branch): User asks about NYC attractions")
    result = await Runner.run(
        agent,
        "What are some famous attractions in New York?",
        session=session,
    )
    logger.info(f"Assistant: {result.final_output}")
    await session.store_run_usage(result)

    # Show the new conversation
    logger.info("\n=== New Conversation Branch ===")
    new_conversation = await session.get_items()
    logger.info("New conversation with branch:")
    for i, item in enumerate(new_conversation, 1):
        role = str(item.get("role", item.get("type", "unknown")))
        if item.get("type") == "function_call":
            content = f"{item.get('name', 'unknown')}({item.get('arguments', '{}')})"
        elif item.get("type") == "function_call_output":
            content = str(item.get("output", ""))
        else:
            content = str(item.get("content", item.get("output", "")))
        logger.info(f"  {i}. {role}: {content}")

    logger.info(f"\nTotal items in new branch: {len(new_conversation)}")

    # === PART 4: Branch Management ===
    logger.info("\n=== PART 4: Branch Management ===")
    # Show all branches
    branches = await session.list_branches()
    logger.info("All branches in this session:")
    for branch in branches:
        current = " (current)" if branch["is_current"] else ""
        logger.info(
            f"  {branch['branch_id']}: {branch['user_turns']} user turns, {branch['message_count']} total messages{current}"
        )

    # Show conversation turns in current branch
    logger.info("\nConversation turns in current branch:")
    current_turns = await session.get_conversation_turns()
    for turn in current_turns:
        logger.info(f"  Turn {turn['turn']}: {turn['content']}")

    logger.info("\n=== Branch Switching Demo ===")
    logger.info("We can switch back to the main branch...")

    # Switch back to main branch
    await session.switch_to_branch("main")

    logger.info("Switched to main branch")

    # Show what's in main branch
    main_items = await session.get_items()
    logger.info(f"Items in main branch: {len(main_items)}")

    # Switch back to new branch
    await session.switch_to_branch(branch_id)
    branch_items = await session.get_items()
    logger.info(f"Items in new branch: {len(branch_items)}")

    logger.info("\n=== Final Summary ===")
    await session.switch_to_branch("main")
    main_final = len(await session.get_items())
    await session.switch_to_branch(branch_id)
    branch_final = len(await session.get_items())

    logger.info(f"Main branch items: {main_final}")
    logger.info(f"New branch items: {branch_final}")

    # Show that branches are completely independent
    logger.info("\nBranches are completely independent:")
    logger.info("- Main branch has full original conversation")
    logger.info("- New branch has turn 1 + new conversation path")
    logger.info("- No interference between branches!")

    logger.info("\n=== Comprehensive Example Complete ===")
    logger.info("This demonstrates the full AdvancedSQLiteSession capabilities!")
    logger.info("Key features:")
    logger.info("- Structured conversation tracking with usage analytics")
    logger.info("- Turn-based organization and querying")
    logger.info("- Create branches from any user message")
    logger.info("- Branches inherit conversation history up to the branch point")
    logger.info("- Complete branch isolation - no interference between branches")
    logger.info("- Easy branch switching and management")
    logger.info("- No complex soft deletion - clean branch-based architecture")
    logger.info("- Perfect for building AI systems with conversation editing capabilities!")

    # Cleanup
    session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
