#!/usr/bin/env python3
"""
OpenAI Assistant Agent CLI
==========================

Command-line interface for the OpenAI Assistant Agent with MCP integration.

Usage:
    python openai_assistant_cli.py --help
"""

import asyncio
import json
import logging
import os
import pickle
import sys
from typing import Optional

import click
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

try:
    from openai_assistant_agent import OpenAIAssistantAgent
except ImportError as e:
    logger.error(f"Failed to import OpenAIAssistantAgent: {e}")
    logger.error("Make sure openai_assistant_agent.py is in the same directory")
    sys.exit(1)


def save_agent_state(agent: OpenAIAssistantAgent, filename: str = "agent_state.json") -> None:
    """Save agent state to JSON file"""
    try:
        state = {
            'config_file': agent.config_file,
            'assistant_id': agent.assistant_id,
            'vector_store_id': agent.vector_store_id,
            'api_key': agent.api_key,
            'mcp_servers_initialized': len(agent.mcp_servers) > 0
        }
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save agent state: {e}")


def load_agent_state(filename: str = "agent_state.json") -> Optional[dict]:
    """Load agent state from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.warning(f"Failed to load agent state: {e}")
        return None


def recreate_agent_from_state(state: dict) -> Optional[OpenAIAssistantAgent]:
    """Recreate agent from saved state"""
    try:
        agent = OpenAIAssistantAgent(state['config_file'])

        # Reinitialize MCP servers if they were initialized before
        if state.get('mcp_servers_initialized', False):
            async def _reinit():
                success = await agent.initialize_mcp_servers()
                if success:
                    agent.create_agent()
                    # Ensure MCP servers stay connected
                    for server in agent.mcp_servers:
                        try:
                            await server.connect()
                        except Exception as e:
                            logger.warning(f"Failed to reconnect to {server.name}: {e}")
                return agent
            return asyncio.run(_reinit())
        else:
            agent.create_agent()
            return agent
    except Exception as e:
        logger.warning(f"Failed to recreate agent from state: {e}")
        return None


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """OpenAI Assistant Agent with MCP Integration"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.ensure_object(dict)


@cli.command()
@click.option('--servers', multiple=True, help='Specific MCP servers to initialize')
@click.pass_context
def init(ctx, servers):
    """Initialize the OpenAI Assistant Agent with MCP servers"""
    agent = OpenAIAssistantAgent()

    server_list = list(servers) if servers else None

    async def _init():
        click.echo("🚀 Initializing OpenAI Assistant Agent...")

        # Initialize MCP servers
        mcp_success = await agent.initialize_mcp_servers(server_list)

        # Create the agent
        agent_success = agent.create_agent()

        if agent_success:
            click.echo("✅ OpenAI Assistant Agent initialized successfully")

            # Show available tools
            tools = await agent.list_available_tools()
            click.echo("\n🔧 Available Tools:")
            for server_name, server_tools in tools.items():
                click.echo(f"  {server_name}: {len(server_tools)} tools")
                if server_tools:
                    for tool in server_tools[:3]:
                        click.echo(f"    • {tool}")
                    if len(server_tools) > 3:
                        click.echo(f"    ... and {len(server_tools) - 3} more")

            # Save agent state
            save_agent_state(agent)
            click.echo("💾 Agent state saved")
        else:
            click.echo("❌ Failed to initialize agent")
            sys.exit(1)

    asyncio.run(_init())


@cli.command()
@click.argument('query')
@click.option('--thread-id', help='OpenAI thread ID for conversation continuity')
@click.option('--output-file', help='Save response to JSON file')
@click.pass_context
def query(ctx, query, thread_id, output_file):
    """Run a query using the OpenAI Assistant Agent"""
    state = load_agent_state()
    if not state:
        click.echo("❌ Agent not initialized. Run 'init' first.")
        sys.exit(1)

    agent = recreate_agent_from_state(state)
    if not agent:
        click.echo("❌ Failed to recreate agent. Run 'init' first.")
        sys.exit(1)

    async def _query():
        click.echo(f"🤖 Processing: {query}")

        result = await agent.run_query(query, thread_id)

        if result:
            click.echo("\n📝 Response:")
            click.echo("=" * 50)
            click.echo(result['response'])

            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"\n💾 Response saved to {output_file}")
        else:
            click.echo("❌ Query failed")
            sys.exit(1)

    asyncio.run(_query())


@cli.command()
@click.argument('server_name')
@click.pass_context
def test_server(ctx, server_name):
    """Test connection to a specific MCP server"""
    agent = OpenAIAssistantAgent()

    async def _test():
        success = await agent.test_mcp_server(server_name)
        if success:
            click.echo(f"✅ {server_name} is working correctly")
        else:
            click.echo(f"❌ {server_name} failed to connect")
            sys.exit(1)

    asyncio.run(_test())


@cli.command()
@click.pass_context
def tools(ctx):
    """List available tools from MCP servers"""
    state = load_agent_state()
    if not state:
        click.echo("❌ Agent not initialized. Run 'init' first.")
        sys.exit(1)

    agent = recreate_agent_from_state(state)
    if not agent:
        click.echo("❌ Failed to recreate agent. Run 'init' first.")
        sys.exit(1)

    async def _list_tools():
        tools = await agent.list_available_tools()

        click.echo("🔧 Available Tools by Server:")
        click.echo("=" * 40)

        for server_name, server_tools in tools.items():
            click.echo(f"\n📡 {server_name} ({len(server_tools)} tools):")
            if server_tools:
                for tool in server_tools:
                    click.echo(f"  • {tool}")
            else:
                click.echo("  No tools available")

    asyncio.run(_list_tools())


@cli.command()
@click.pass_context
def info(ctx):
    """Show information about the OpenAI Assistant Agent"""
    agent = ctx.obj.get('agent')
    if not agent:
        click.echo("❌ Agent not initialized. Run 'init' first.")
        sys.exit(1)

    click.echo("🤖 OpenAI Assistant Agent Information")
    click.echo("=" * 40)
    click.echo(f"Assistant ID: {agent.assistant_id}")
    click.echo(f"Vector Store ID: {agent.vector_store_id}")
    click.echo(f"API Key: {agent.api_key[:20]}...")
    click.echo(f"MCP Servers: {len(agent.mcp_servers)} connected")

    if agent.mcp_servers:
        click.echo("\n🔗 Connected MCP Servers:")
        for server in agent.mcp_servers:
            click.echo(f"  • {server.name}")


@cli.command()
@click.pass_context
def cleanup(ctx):
    """Clean up MCP server connections"""
    agent = ctx.obj.get('agent')
    if not agent:
        click.echo("❌ Agent not initialized.")
        return

    async def _cleanup():
        await agent.cleanup()
        click.echo("✅ Cleanup completed")

    asyncio.run(_cleanup())


@cli.command()
def demo():
    """Run a demonstration of the OpenAI Assistant Agent"""
    click.echo("🚀 Running OpenAI Assistant Agent Demo...")

    async def _demo():
        # Import and run the main demo function
        try:
            from openai_assistant_agent import main as demo_main
            await demo_main()
        except Exception as e:
            click.echo(f"❌ Demo failed: {e}")
            sys.exit(1)

    asyncio.run(_demo())


if __name__ == "__main__":
    cli()