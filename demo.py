#!/usr/bin/env python3
"""
Demo script showing the MCP Client app functionality
"""

import asyncio
import sys
import logging
from mcp_client import MCPClient, MCPClientConfig

logger = logging.getLogger(__name__)

async def demo_app():
    """Demonstrate the MCP client app functionality"""

    logger.info("🚀 MCP Client Application Demo")
    logger.info("%s", "=" * 50)

    # Initialize configuration
    config = MCPClientConfig()
    client = MCPClient(config)

    logger.info("1️⃣ Configuration loaded successfully")
    servers = config.get_server_configs()
    logger.info("   📊 Found %d configured servers", len(servers))

    # Try to initialize servers (will fail due to auth, but shows error handling)
    logger.info("\n2️⃣ Attempting to initialize MCP servers...")
    logger.info("   Note: This will fail due to missing authentication tokens (expected)")

    success = await client.initialize_servers()
    if success:
        logger.info("   ✅ Servers initialized successfully")
    else:
        logger.warning("   ⚠️ Server initialization failed (expected - no auth tokens)")
        logger.info("   📝 This demonstrates proper error handling")

    # Create agent with fake model (works without MCP servers)
    logger.info("\n3️⃣ Creating agent with fake model...")
    success = client.create_agent()
    if success:
        logger.info("   ✅ Agent created successfully with fake model")
        logger.info("   🤖 Agent is ready for queries (using fake responses)")
    else:
        logger.error("   ❌ Failed to create agent")

    # Demonstrate query functionality
    if client.agent:
        logger.info("\n4️⃣ Running demo query...")
        query = "Hello! Can you tell me about MCP (Model Context Protocol)?"
        logger.info("   Query: %s", query)

        try:
            result = await client.run_query(query)
            logger.info("   📝 Response:")
            logger.info("   %s", result)
        except Exception as e:
            logger.error("   ❌ Query failed: %s", e)

    # Clean up
    logger.info("\n5️⃣ Cleaning up...")
    await client.cleanup()
    logger.info("   ✅ Cleanup completed")

    logger.info("\n🎉 Demo completed successfully!")
    logger.info("\n💡 To use with real MCP servers:")
    logger.info("   1. Set valid authentication tokens in .env")
    logger.info("   2. Run: python mcp_client.py init")
    logger.info("   3. Run: python mcp_client.py create-agent")
    logger.info("   4. Run: python mcp_client.py query 'Your question here'")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_app())