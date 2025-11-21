#!/usr/bin/env python3
"""
OpenAI Assistant Agent with Vector Store Integration
====================================================

This agent integrates an OpenAI Assistant with vector store capabilities
and MCP (Model Context Protocol) for external service access.

Assistant ID: asst_70Xrb6BnK0CtVx3qm89J6nEQ
Vector Store ID: vs_1BREGwaFlfMYaIIOlzW7xCuC
"""

import asyncio
import json
import logging
import os
from typing import Optional, Dict, Any

from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from openai import OpenAI

# Suppress MCP-related asyncio cleanup errors
class MCPAsyncioFilter(logging.Filter):
    def filter(self, record):
        if record.name == 'asyncio' and record.levelno == logging.ERROR:
            message = record.getMessage()
            # Suppress MCP stdio client cleanup errors
            if ('cancel scope' in message or
                'GeneratorExit' in message or
                'stdio_client' in message):
                return False
        return True

# Add filter to asyncio logger
asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.addFilter(MCPAsyncioFilter())

logger = logging.getLogger(__name__)


class OpenAIAssistantAgent:
    """OpenAI Assistant Agent with MCP integration"""

    def __init__(self, config_file: str = "openai_assistant_config.json"):
        self.config_file = config_file
        self.mcp_servers = []
        self.agent = None
        self.openai_client = None
        self.config = {}

        # Load configuration
        self._load_config()

        # OpenAI Assistant credentials from config
        self.assistant_id = self.config.get('openai_assistant', {}).get('assistant_id', '')
        self.vector_store_id = self.config.get('openai_assistant', {}).get('vector_store_id', '')
        self.api_key = self.config.get('openai_assistant', {}).get('api_key', '')

        # Initialize OpenAI client
        self._init_openai_client()

    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info("✅ Configuration loaded from %s", self.config_file)
        except FileNotFoundError:
            logger.warning("⚠️  Config file %s not found, using defaults", self.config_file)
            self.config = {}
        except json.JSONDecodeError as e:
            logger.error("❌ Invalid JSON in config file: %s", e)
            self.config = {}

    def _init_openai_client(self) -> None:
        """Initialize OpenAI client with provided API key"""
        try:
            self.openai_client = OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI client initialized successfully")
        except Exception as e:
            logger.error("❌ Failed to initialize OpenAI client: %s", e)
            raise

    async def initialize_mcp_servers(self, server_names: Optional[list[str]] = None) -> bool:
        """Initialize MCP servers for external service access"""
        try:
            # Get MCP servers from config
            mcp_config = self.config.get('mcp_servers', {})

            if not mcp_config:
                logger.warning("⚠️  No MCP servers configured - proceeding without external tools")
                return True

            servers_to_init = server_names or list(mcp_config.keys())

            for server_name in servers_to_init:
                if server_name in mcp_config:
                    server_config = mcp_config[server_name]

                    logger.info("🔧 Initializing MCP server: %s", server_name)

                    try:
                        mcp_server = MCPServerStdio(
                            params=MCPServerStdioParams(
                                command=server_config["command"],
                                args=server_config.get("args", []),
                                env=server_config.get("env", {}),
                            ),
                            name=server_name
                        )

                        # Connect to the MCP server with timeout
                        await asyncio.wait_for(mcp_server.connect(), timeout=10.0)
                        self.mcp_servers.append(mcp_server)
                        logger.info("✅ Connected to %s", server_name)

                    except asyncio.TimeoutError:
                        logger.warning("⚠️  Timeout connecting to %s - skipping", server_name)
                        continue
                    except Exception as e:
                        logger.warning("⚠️  Failed to connect to %s: %s - skipping", server_name, e)
                        continue

            if not self.mcp_servers:
                logger.warning("⚠️  No MCP servers connected - proceeding without external tools")
                return True

            logger.info("✅ Initialized %d MCP servers", len(self.mcp_servers))
            return True

        except Exception as e:
            logger.error("❌ Failed to initialize MCP servers: %s", e)
            return False

    async def test_mcp_server(self, server_name: str) -> bool:
        """Test connection to a specific MCP server"""
        try:
            mcp_config = self.config.get('mcp_servers', {})

            if server_name not in mcp_config:
                logger.error("❌ MCP server '%s' not found in configuration", server_name)
                return False

            server_config = mcp_config[server_name]
            logger.info("🔧 Testing MCP server: %s", server_name)

            mcp_server = MCPServerStdio(
                params=MCPServerStdioParams(
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    env=server_config.get("env", {}),
                ),
                name=server_name
            )

            # Try to connect with timeout
            await asyncio.wait_for(mcp_server.connect(), timeout=5.0)
            logger.info("✅ Successfully connected to %s", server_name)

            # Try to list tools
            tools = await mcp_server.list_tools()
            logger.info("📋 %s has %d tools available", server_name, len(tools))

            return True

        except asyncio.TimeoutError:
            logger.error("❌ Timeout connecting to %s", server_name)
            return False
        except Exception as e:
            logger.error("❌ Failed to connect to %s: %s", server_name, e)
            return False

    def create_agent(self) -> bool:
        """Create the OpenAI Assistant agent with MCP integration"""
        try:
            # Try to verify OpenAI Assistant exists and is accessible
            assistant_available = False
            if self.openai_client:
                try:
                    assistant = self.openai_client.beta.assistants.retrieve(self.assistant_id)
                    logger.info("✅ Connected to OpenAI Assistant: %s", assistant.name)
                    assistant_available = True
                except Exception as e:
                    logger.warning("⚠️  OpenAI Assistant not found: %s", e)
                    logger.info("   Falling back to standard Agents SDK implementation")

            # Check vector store access
            vector_store_available = False
            if self.openai_client:
                try:
                    vector_store = self.openai_client.beta.vector_stores.retrieve(self.vector_store_id)
                    logger.info("✅ Connected to Vector Store: %s", vector_store.name)
                    vector_store_available = True
                except Exception as e:
                    logger.warning("⚠️  Vector store access issue: %s", e)

            # Create agent with appropriate configuration
            if assistant_available:
                # Use OpenAI Assistant with MCP integration
                agent_config = {
                    "name": "OpenAI Assistant Agent",
                    "instructions": f"""
                    You are an advanced AI assistant powered by OpenAI with access to external services.

                    Your capabilities include:
                    - OpenAI Assistant with ID: {self.assistant_id}
                    - Vector Store access for knowledge retrieval (ID: {self.vector_store_id})
                    - External tools via MCP (Model Context Protocol) servers
                    - File operations, API calls, and system commands

                    When answering questions:
                    1. Use your vector store knowledge for context
                    2. Leverage MCP tools for external data access
                    3. Provide clear, actionable responses
                    4. Explain your reasoning when using tools

                    Available MCP servers: {len(self.mcp_servers)} connected
                    """,
                    "model_settings": ModelSettings(
                        temperature=0.7,
                        tool_choice="auto"
                    )
                }
            else:
                # Fallback to standard Agents SDK agent
                logger.info("🔄 Using standard Agents SDK agent with MCP integration")

                # Check if we have a valid API key for the model
                api_key = os.getenv('OPENAI_API_KEY') or self.api_key
                if not api_key or api_key == self.api_key[:20] + '...':  # Check if it's our placeholder
                    logger.warning("⚠️  No valid OpenAI API key found. Using fake model for testing.")
                    from tests.fake_model import FakeModel
                    model = FakeModel()
                else:
                    # Try to use OpenAI model, fallback to default if not available
                    try:
                        from agents import OpenAIProvider
                        provider = OpenAIProvider(api_key=api_key)
                        model = provider.get_model("gpt-4o")
                    except ImportError:
                        logger.warning("⚠️  OpenAIProvider not available, using default model")
                        from agents.models import get_default_model
                        model = get_default_model()

                agent_config = {
                    "name": "MCP-Enhanced Agent",
                    "instructions": f"""
                    You are an AI assistant with access to external services through the MCP (Model Context Protocol).

                    Your capabilities include:
                    - External tools via MCP servers for data access and operations
                    - File system operations and command execution
                    - API integrations with various external services
                    - Knowledge retrieval and processing

                    When using tools, be specific about what you're trying to accomplish.
                    If you encounter any issues, explain them clearly to the user.

                    Available MCP servers: {len(self.mcp_servers)} connected
                    """,
                    "model": model,
                    "model_settings": ModelSettings(
                        temperature=0.7,
                        tool_choice="auto"
                    )
                }

            if self.mcp_servers:
                agent_config["mcp_servers"] = self.mcp_servers

            self.agent = Agent(**agent_config)

            logger.info("✅ Agent created successfully")
            if assistant_available:
                logger.info("   Mode: OpenAI Assistant with MCP integration")
            else:
                logger.info("   Mode: Standard Agents SDK with MCP integration")
            return True

        except Exception as e:
            logger.error("❌ Failed to create agent: %s", e)
            return False

    async def run_query(self, query: str, thread_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Run a query using the OpenAI Assistant with MCP tools"""
        try:
            if not self.agent:
                logger.error("❌ Agent not initialized")
                return None

            logger.info("🤖 Processing query: %s", query)

            # Ensure MCP servers are connected before running the query
            if self.mcp_servers:
                logger.info("🔗 Ensuring %d MCP servers are connected...", len(self.mcp_servers))
                for server in self.mcp_servers:
                    try:
                        # Check if server is connected, reconnect if needed
                        if not hasattr(server, '_connected') or not server._connected:
                            await asyncio.wait_for(server.connect(), timeout=10.0)
                            logger.info("✅ Reconnected to %s", server.name)
                        else:
                            logger.info("✅ %s already connected", server.name)
                    except Exception as e:
                        logger.warning("⚠️  Failed to connect to %s: %s", server.name, e)
                        # Remove failed server from the list
                        self.mcp_servers.remove(server)

            # Use the OpenAI Agents SDK Runner
            result = await Runner.run(
                starting_agent=self.agent,
                input=query
            )

            response = {
                "query": query,
                "response": result.final_output,
                "thread_id": thread_id,
                "timestamp": asyncio.get_event_loop().time()
            }

            logger.info("✅ Query completed successfully")
            return response

        except Exception as e:
            logger.error("❌ Query failed: %s", e)
            return None

    async def list_available_tools(self) -> Dict[str, list[str]]:
        """List all available tools from MCP servers"""
        tools = {}

        # Get MCP servers from config
        mcp_config = self.config.get('mcp_servers', {})

        for server_name in mcp_config.keys():
            try:
                logger.info("🔍 Testing tools for %s...", server_name)
                server_config = mcp_config[server_name]

                # Create a temporary connection to test tools
                mcp_server = MCPServerStdio(
                    params=MCPServerStdioParams(
                        command=server_config["command"],
                        args=server_config.get("args", []),
                        env=server_config.get("env", {}),
                    ),
                    name=server_name
                )

                # Connect temporarily
                await asyncio.wait_for(mcp_server.connect(), timeout=10.0)

                # List tools
                server_tools = await mcp_server.list_tools()
                logger.debug("📋 Raw tools result for %s: %s", server_name, type(server_tools))

                # Extract tool names - assume it's a list of tool objects
                try:
                    if isinstance(server_tools, list):
                        tool_names = [getattr(tool, 'name', str(tool)) for tool in server_tools]
                    else:
                        # Try to get tools attribute if it exists
                        tools_list = getattr(server_tools, 'tools', server_tools)
                        if isinstance(tools_list, list):
                            tool_names = [getattr(tool, 'name', str(tool)) for tool in tools_list]
                        else:
                            tool_names = []
                except Exception:
                    tool_names = []

                tools[server_name] = tool_names
                logger.info("✅ Found %d tools for %s", len(tool_names), server_name)

            except asyncio.TimeoutError:
                logger.warning("⚠️  Timeout connecting to %s for tools listing", server_name)
                tools[server_name] = []
            except Exception as e:
                logger.warning("⚠️  Failed to list tools for %s: %s: %s", server_name, type(e).__name__, e)
                tools[server_name] = []

        return tools

    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            for server in self.mcp_servers:
                try:
                    await server.cleanup()
                    logger.info("🧹 Cleaned up %s", server.name)
                except Exception as e:
                    # Suppress asyncio cleanup errors that don't affect functionality
                    error_msg = str(e)
                    if "cancel scope" in error_msg or "GeneratorExit" in error_msg:
                        logger.info("🧹 Cleaned up %s (cleanup warnings suppressed)", server.name)
                    else:
                        logger.warning("⚠️  Error cleaning up %s: %s", server.name, e)

            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error("❌ Cleanup failed: %s", e)


async def main():
    """Main function to demonstrate the OpenAI Assistant Agent"""
    logger.info("🚀 Starting OpenAI Assistant Agent with MCP Integration")
    logger.info("%s", "=" * 60)

    # Initialize the agent
    assistant_agent = OpenAIAssistantAgent()

    # Initialize MCP servers
    logger.info("\n🔗 Initializing MCP servers...")
    mcp_success = await assistant_agent.initialize_mcp_servers()

    # Create the agent
    logger.info("\n🤖 Creating agent...")
    agent_success = assistant_agent.create_agent()

    if not agent_success:
        logger.error("❌ Failed to create agent")
        return

    # List available tools
    logger.info("\n🔧 Checking available tools...")
    tools = await assistant_agent.list_available_tools()
    for server_name, server_tools in tools.items():
        logger.info("  %s: %d tools", server_name, len(server_tools))
        if server_tools:
            for tool in server_tools[:3]:  # Show first 3 tools
                logger.info("    • %s", tool)
            if len(server_tools) > 3:
                logger.info("    ... and %d more", len(server_tools) - 3)

    # Example queries to demonstrate capabilities
    example_queries = [
        "What external services are available through the MCP servers?",
        "Can you help me access data from connected services?",
        "Show me what tools you have access to"
    ]

    logger.info("\n💬 Running %d example queries...", len(example_queries))
    logger.info("%s", "-" * 40)

    for i, query in enumerate(example_queries, 1):
        logger.info("\nQuery %d: %s", i, query)
        result = await assistant_agent.run_query(query)
        if result:
            logger.info("Response: %s...", result['response'][:200])
        else:
            logger.error("❌ Query failed")

    # Cleanup
    await assistant_agent.cleanup()
    logger.info("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    # Ensure basic logging configuration when run as a script
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())