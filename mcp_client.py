#!/usr/bin/env python3
"""
Production-Ready MCP Client Application
=======================================

A comprehensive MCP (Model Context Protocol) client that integrates with the OpenAI Agents SDK.
This application demonstrates production-ready patterns for MCP server integration.

Features:
- Multiple MCP server support (HTTP Streamable, Stdio)
- Authentication handling
- Error recovery and logging
- Configuration management
- CLI interface
- Production deployment ready

Usage:
    python mcp_client.py --help
"""

import asyncio
import json
import logging
import os
import re
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_client.log', encoding='utf-8'),
    ],
)
logger = logging.getLogger(__name__)

# Suppress noisy asyncio shutdown warnings from underlying MCP clients.
logging.getLogger("asyncio").setLevel(logging.CRITICAL)


_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")

try:
    from agents import Agent, Runner
    from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
    from agents.mcp import MCPServerStdio, MCPServerStdioParams
    from agents.model_settings import ModelSettings
except ImportError as e:
    logger.error(f"Failed to import OpenAI Agents SDK: {e}")
    logger.error("Please ensure the OpenAI Agents SDK is properly installed")
    sys.exit(1)


class MCPClientConfig:
    """Configuration management for MCP servers"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "mcp_config.json"
        self.servers = {}
        self.load_config()

    def load_config(self) -> None:
        """Load MCP server configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.servers = config.get('servers', {})
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config from {self.config_file}: {e}")
        else:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self._load_default_config()

    def _load_default_config(self) -> None:
        """Load default MCP server configurations"""
        self.servers = {
            "cloudmcp-server-6837335c7e6338": {
                "url": "https://18268932-6837335c7e6338.router.cloudmcp.run/mcp",
                "headers": {"Authorization": f"Bearer {os.getenv('CLOUDMCP_TOKEN', 'your-token')}"},
                "type": "http",
                "timeout": 30
            },
            "cloudmcp-server-48e7550c72e668": {
                "command": "npx",
                "args": ["mcp-remote", "https://18268932-48e7550c72e668.router.cloudmcp.run/mcp"],
                "env": {},
                "type": "stdio"
            }
        }

    def get_server_configs(self) -> Dict[str, Dict]:
        """Get all server configurations"""
        return self.servers

    def get_server_config(self, name: str) -> Optional[Dict]:
        """Get configuration for a specific server"""
        return self.servers.get(name)


class MCPClient:
    """Production-ready MCP client"""

    def __init__(self, config: MCPClientConfig):
        self.config = config
        self.mcp_servers = []
        self.agent = None

    async def initialize_servers(self, server_names: Optional[List[str]] = None) -> bool:
        """Initialize MCP servers"""
        try:
            server_configs = self.config.get_server_configs()

            config_dir = Path(self.config.config_file).resolve().parent

            missing_env_vars: set[str] = set()

            def interpolate(value: str) -> str:
                def repl(match: re.Match[str]) -> str:
                    var = match.group(1)
                    env_val = os.getenv(var)
                    if env_val is None:
                        missing_env_vars.add(var)
                        return match.group(0)
                    return env_val

                return _ENV_VAR_PATTERN.sub(repl, value)

            def is_single_placeholder(value: str) -> Optional[str]:
                m = _ENV_VAR_PATTERN.fullmatch(value)
                return m.group(1) if m else None

            if server_names:
                # Filter to specified servers
                server_configs = {name: config for name, config in server_configs.items()
                                if name in server_names}

            for server_name, server_config in server_configs.items():
                # Allow disabling misbehaving servers via config.
                if not server_config.get("enabled", True):
                    logger.info(f"Skipping disabled MCP server: {server_name}")
                    continue

                logger.info(f"Initializing MCP server: {server_name}")

                try:
                    if server_config.get('type') == 'http' or 'url' in server_config:
                        # HTTP Streamable MCP Server
                        params: MCPServerStreamableHttpParams = {
                            "url": interpolate(server_config["url"]),
                            "headers": {
                                k: interpolate(v) if isinstance(v, str) else v
                                for k, v in server_config.get("headers", {}).items()
                            },
                            "timeout": server_config.get("timeout", 30),
                            "sse_read_timeout": server_config.get("sse_read_timeout", 60),
                        }

                        server = MCPServerStreamableHttp(
                            params=params,
                            name=server_name,
                            cache_tools_list=True
                        )

                    else:
                        # Stdio MCP Server
                        raw_env = server_config.get("env", {})
                        resolved_env: dict[str, str] = {}
                        for key, value in raw_env.items():
                            if not isinstance(value, str):
                                continue
                            placeholder_var = is_single_placeholder(value)
                            if placeholder_var is not None and os.getenv(placeholder_var) is None:
                                missing_env_vars.add(placeholder_var)
                                continue
                            resolved_env[key] = interpolate(value)

                        resolved_args: list[str] = []
                        for arg in server_config.get("args", []):
                            resolved_args.append(interpolate(arg) if isinstance(arg, str) else arg)

                        cwd = server_config.get("cwd")
                        if isinstance(cwd, str) and not os.path.isabs(cwd):
                            cwd = str((config_dir / cwd).resolve())
                        elif cwd is None:
                            cwd = str(config_dir)

                        params: MCPServerStdioParams = {
                            "command": server_config["command"],
                            "args": resolved_args,
                            "env": resolved_env,
                            "cwd": cwd,
                            "encoding": server_config.get("encoding", "utf-8"),
                            "encoding_error_handler": server_config.get(
                                "encoding_error_handler", "strict"
                            ),
                        }

                        server = MCPServerStdio(
                            params=params,
                            name=server_name
                        )

                    # Connect to the server
                    await server.connect()
                    self.mcp_servers.append(server)
                    logger.info(f"✅ Successfully connected to {server_name}")

                except asyncio.CancelledError as e:
                    logger.error(f"❌ Initialization cancelled for {server_name}: {e}")
                    # Continue with other servers instead of failing completely
                    continue
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {server_name}: {e}")
                    # Continue with other servers instead of failing completely
                    continue

            if not self.mcp_servers:
                logger.error("No MCP servers were successfully initialized")
                return False

            if missing_env_vars:
                logger.warning(
                    "Some MCP config env vars were not set: %s",
                    ", ".join(sorted(missing_env_vars)),
                )

            logger.info(f"Successfully initialized {len(self.mcp_servers)} MCP servers")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
            return False

    def create_agent(self, model_name: str = "gpt-4o") -> bool:
        """Create an agent with MCP servers"""
        try:
            if not self.mcp_servers:
                logger.error("No MCP servers available. Initialize servers first.")
                return False

            # Optional override: allow forcing the local FakeModel even when
            # an OpenAI API key is present. This is useful when the project
            # does not have access to a given model or for offline testing.
            use_fake_env = os.getenv("MCP_CLIENT_USE_FAKE_MODEL", "").lower()
            use_fake_model = use_fake_env in {"1", "true", "yes"}

            # Check if we have a real OpenAI API key
            api_key = os.getenv('OPENAI_API_KEY')
            if use_fake_model or not api_key or api_key == 'your_openai_api_key_here':
                if not api_key or api_key == 'your_openai_api_key_here':
                    logger.warning("OpenAI API key not configured. Using fake model for testing.")
                else:
                    logger.info("MCP_CLIENT_USE_FAKE_MODEL is set; using FakeModel instead of calling OpenAI.")

                from tests.fake_model import FakeModel
                model = FakeModel()
            else:
                # Use real OpenAI model
                from agents import OpenAIProvider
                provider = OpenAIProvider(api_key=api_key)
                model = provider.get_model(model_name)

            self.agent = Agent(
                name="MCP Production Agent",
                instructions="""
                You are a helpful AI assistant with access to external tools via MCP (Model Context Protocol).

                Available tools:
                - Use the tools from connected MCP servers to help answer questions
                - Be informative and provide detailed responses
                - If you encounter errors, explain them clearly

                Always strive to provide the most accurate and helpful information possible.
                """,
                mcp_servers=self.mcp_servers,
                model=model,
                model_settings=ModelSettings(
                    temperature=0.7,
                    tool_choice="auto"
                )
            )

            logger.info("✅ Agent created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return False

    async def run_query(self, query: str) -> Optional[str]:
        """Run a query using the MCP-enabled agent"""
        try:
            if not self.agent:
                logger.error("Agent not initialized. Create agent first.")
                return None

            logger.info(f"Running query: {query}")

            # For time-sensitive requests (e.g., "latest news"), prefer a deterministic MCP web-search
            # call so results are current and we don't rely on the model choosing tools.
            if re.search(
                r"\b(latest|today|current|breaking|headline|headlines|news|as of|right now|this week|this month)\b",
                query,
                re.IGNORECASE,
            ):
                for server in self.mcp_servers:
                    try:
                        server_tools = await server.list_tools()
                        available = {tool.name for tool in server_tools}
                        for tool_name in ("tavily_search", "web_search"):
                            if tool_name in available:
                                tool_result = await server.call_tool(tool_name, {"query": query})
                                payload = getattr(tool_result, "structured_content", None)
                                if payload is None:
                                    payload = getattr(tool_result, "content", tool_result)
                                return (
                                    f"Web search results via {server.name}/{tool_name}:\n"
                                    + json.dumps(payload, ensure_ascii=False, default=str, indent=2)[:4000]
                                )
                    except Exception as e:
                        logger.info(f"Web-search short-circuit skipped for {server.name}: {e}")

            # Use a timeout for the query
            result = await asyncio.wait_for(
                Runner.run(starting_agent=self.agent, input=query),
                timeout=300  # 5 minute timeout
            )

            response = result.final_output
            logger.info("Query completed successfully")
            return response

        except asyncio.TimeoutError:
            logger.error("Query timed out after 5 minutes")
            return "Sorry, the query timed out. Please try again with a simpler request."
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Sorry, an error occurred while processing your request: {str(e)}"

    async def list_tools(self) -> Dict[str, List[str]]:
        """List available tools from all MCP servers"""
        tools = {}
        try:
            for server in self.mcp_servers:
                try:
                    server_tools = await server.list_tools()
                    tools[server.name] = [tool.name for tool in server_tools]
                except Exception as e:
                    logger.warning(f"Failed to list tools for {server.name}: {e}")
                    tools[server.name] = []
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")

        return tools

    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            for server in self.mcp_servers:
                try:
                    await server.disconnect()
                except Exception as e:
                    logger.warning(f"Error disconnecting {server.name}: {e}")
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


@click.group()
@click.option('--config', default='mcp_config.json', help='Path to MCP configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """MCP Client - Production-ready MCP integration with OpenAI Agents SDK"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj['config'] = MCPClientConfig(config)
    ctx.obj['client'] = MCPClient(ctx.obj['config'])


@cli.command()
@click.pass_context
def list_servers(ctx):
    """List available MCP servers"""
    config = ctx.obj['config']
    servers = config.get_server_configs()

    click.echo("📋 Available MCP Servers:")
    click.echo("=" * 40)

    for name, server_config in servers.items():
        server_type = server_config.get('type', 'stdio')
        click.echo(f"🔧 {name} ({server_type})")

        if 'url' in server_config:
            click.echo(f"   URL: {server_config['url']}")
        elif 'command' in server_config:
            args = ' '.join(server_config.get('args', []))
            click.echo(f"   Command: {server_config['command']} {args}")

        click.echo()


@cli.command()
@click.option('--servers', multiple=True, help='Specific servers to initialize (default: all)')
@click.pass_context
def init(ctx, servers):
    """Initialize MCP servers"""
    client = ctx.obj['client']
    server_list = list(servers) if servers else None

    async def _init():
        success = await client.initialize_servers(server_list)
        if success:
            click.echo(f"✅ Initialized {len(client.mcp_servers)} MCP servers")

            # List available tools
            tools = await client.list_tools()
            click.echo("\n🔧 Available Tools:")
            for server_name, server_tools in tools.items():
                click.echo(f"  {server_name}: {len(server_tools)} tools")
                for tool in server_tools[:5]:  # Show first 5 tools
                    click.echo(f"    - {tool}")
                if len(server_tools) > 5:
                    click.echo(f"    ... and {len(server_tools) - 5} more")
        else:
            click.echo("❌ Failed to initialize MCP servers")
            sys.exit(1)

    asyncio.run(_init())


@cli.command()
@click.option('--model', default='gpt-4.1', help='OpenAI model to use')
@click.pass_context
def create_agent(ctx, model):
    """Create an agent with initialized MCP servers"""
    client = ctx.obj['client']

    # Ensure MCP servers are initialized in this process. The `init` command
    # is useful for inspection, but each CLI invocation is a new process, so
    # we need to initialize servers here as well if none are connected yet.
    if not client.mcp_servers:
        async def _init_servers() -> None:
            success = await client.initialize_servers()
            if not success or not client.mcp_servers:
                click.echo("❌ Failed to initialize MCP servers. Check mcp_config.json and your environment.")
                sys.exit(1)

        asyncio.run(_init_servers())

    success = client.create_agent(model)
    if success:
        click.echo("✅ Agent created successfully")
    else:
        click.echo("❌ Failed to create agent")
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--timeout', default=300, help='Query timeout in seconds')
@click.option('--model', default='gpt-4.1', help='OpenAI model to use')
@click.pass_context
def query(ctx, query, timeout, model):
    """Run a query using MCP servers and an agent (all in one command)."""
    client = ctx.obj['client']

    async def _query():
        try:
            # Ensure MCP servers are initialized.
            if not client.mcp_servers:
                init_success = await client.initialize_servers()
                if not init_success or not client.mcp_servers:
                    click.echo("❌ Failed to initialize MCP servers. Check mcp_config.json and your environment.")
                    sys.exit(1)

            # Ensure an agent exists for this process.
            if not client.agent:
                if not client.create_agent(model):
                    click.echo("❌ Failed to create agent")
                    sys.exit(1)

            result = await asyncio.wait_for(
                client.run_query(query),
                timeout=timeout,
            )
            click.echo("\n🤖 Response:")
            click.echo("=" * 50)
            click.echo(result)
        except asyncio.TimeoutError:
            click.echo(f"❌ Query timed out after {timeout} seconds")
        except Exception as e:
            click.echo(f"❌ Query failed: {e}")

    asyncio.run(_query())


@cli.command()
@click.pass_context
def tools(ctx):
    """List available tools from MCP servers"""
    client = ctx.obj['client']

    async def _list_tools():
        if not client.mcp_servers:
            init_success = await client.initialize_servers()
            if not init_success or not client.mcp_servers:
                click.echo("❌ Failed to initialize MCP servers. Check mcp_config.json and your environment.")
                sys.exit(1)

        tools = await client.list_tools()
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
def cleanup(ctx):
    """Clean up MCP server connections"""
    client = ctx.obj['client']

    async def _cleanup():
        await client.cleanup()
        click.echo("✅ Cleanup completed")

    asyncio.run(_cleanup())


if __name__ == "__main__":
    cli()