#!/usr/bin/env python3
"""
Cloud MCP Router Integration Example
====================================

This example demonstrates how to integrate with external services
via the cloud MCP router using the OpenAI Agents SDK.
"""

import asyncio
import os
import logging
from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStdio, MCPServerStdioParams

logger = logging.getLogger(__name__)


async def main():
    """Demonstrate MCP integration with cloud router"""

    logger.info("🔗 Connecting to Cloud MCP Router...")

    # Configure the MCP server using the cloud router
    mcp_server = MCPServerStdio(
        params=MCPServerStdioParams(
            command="npx",
            args=["mcp-remote", "https://18268932-48e7550c72e668.router.cloudmcp.run/mcp"],
            env={},
        ),
        name="cloud-mcp-router"
    )

    # Connect to the MCP server
    await mcp_server.connect()
    logger.info("✅ Connected to MCP server")

    # Create an agent with access to external services via MCP
    agent = Agent(
        name="Cloud MCP Assistant",
        instructions="""
        You are an AI assistant with access to external services through the MCP (Model Context Protocol).

        Your capabilities include:
        - Accessing external APIs and services via the cloud MCP router
        - Using tools provided by connected MCP servers
        - Processing data from various external sources

        When using tools, be specific about what you're trying to accomplish.
        If you encounter any issues, explain them clearly to the user.
        """,
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(
            temperature=0.7,
            tool_choice="auto"
        )
    )

    logger.info("🤖 Agent created with MCP integration")

    # Example queries to demonstrate external service integration
    queries = [
        "What external services are available through the MCP router?",
        "Can you help me access data from connected services?",
        "Show me what tools are available for external integrations"
    ]

    for i, query in enumerate(queries, 1):
        logger.info("\n--- Query %d: %s ---", i, query)

        try:
            result = await Runner.run(agent, query)
            logger.info("Response: %s", result.final_output)

        except Exception as e:
            logger.error("Error: %s", e)

    # Clean up
    await mcp_server.cleanup()
    logger.info("\n🧹 Cleanup completed")


if __name__ == "__main__":
    # Ensure we have Node.js available for npx
    if not os.system("node --version >nul 2>&1"):
        logger.info("Node.js is available ✓")
    else:
        logger.error("⚠️  Node.js not found. Please install Node.js to use MCP remote servers.")
        exit(1)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())