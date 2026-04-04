#!/usr/bin/env python3
"""
Test script for OpenAI Assistant Agent with Memory Management and MCP Integration
================================================================================

This script demonstrates the enhanced OpenAI Assistant Agent with:
- Memory management with auto-save functionality
- Agent configuration persistence
- Enhanced MCP tool integration with local server support
"""

import asyncio
import json
import logging

from openai_assistant_agent import OpenAIAssistantAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_memory_management():
    """Test memory management features"""
    logger.info("🧠 Testing Memory Management Features")
    logger.info("=" * 50)

    agent = OpenAIAssistantAgent()

    # Test memory stats
    stats = agent.get_memory_stats()
    logger.info("📊 Initial memory stats: %s", json.dumps(stats, indent=2))

    # Test memory updates
    agent.update_memory("test_setting", "test_value")
    agent.update_memory("temperature", 0.8)

    # Test conversation addition
    agent.add_conversation("Hello", "Hi there!", {"test": True})

    # Test recent conversations
    recent = agent.get_recent_conversations(5)
    logger.info("💬 Recent conversations: %d", len(recent))

    # Test auto-save toggle
    agent.toggle_auto_save(False)
    agent.toggle_auto_save(True)

    # Force save
    agent.force_save_memory()

    # Get updated stats
    stats = agent.get_memory_stats()
    logger.info("📊 Updated memory stats: %s", json.dumps(stats, indent=2))


async def test_mcp_integration():
    """Test MCP server integration"""
    logger.info("🔗 Testing MCP Integration")
    logger.info("=" * 50)

    agent = OpenAIAssistantAgent()

    # Initialize MCP servers (will try to add local server)
    logger.info("🔧 Initializing MCP servers...")
    mcp_success = await agent.initialize_mcp_servers()

    if mcp_success:
        logger.info("✅ MCP servers initialized: %d servers", len(agent.mcp_servers))

        # List available tools
        tools = await agent.list_available_tools()
        logger.info("🔧 Available tools from %d servers:", len(tools))
        for server_name, server_tools in tools.items():
            logger.info("  %s: %d tools", server_name, len(server_tools))
    else:
        logger.warning("⚠️  MCP server initialization failed")


async def test_configuration_persistence():
    """Test configuration persistence"""
    logger.info("💾 Testing Configuration Persistence")
    logger.info("=" * 50)

    agent = OpenAIAssistantAgent()

    # Modify configuration
    if "test_config" not in agent.config:
        agent.config["test_config"] = {
            "memory_enabled": True,
            "auto_save_interval": 300,
            "max_conversations": 100,
        }
        agent.save_config()
        logger.info("✅ Test configuration added and saved")

    # Verify configuration was saved
    agent2 = OpenAIAssistantAgent()
    if "test_config" in agent2.config:
        logger.info("✅ Configuration persistence verified")
    else:
        logger.warning("⚠️  Configuration persistence failed")


async def main():
    """Main test function"""
    logger.info("🚀 Testing Enhanced OpenAI Assistant Agent")
    logger.info("=" * 60)

    try:
        # Test memory management
        await test_memory_management()

        # Test MCP integration
        await test_mcp_integration()

        # Test configuration persistence
        await test_configuration_persistence()

        logger.info("✅ All tests completed successfully!")

    except Exception as e:
        logger.error("❌ Test failed: %s", e)
        raise
    finally:
        # Cleanup
        agent = OpenAIAssistantAgent()
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
