#!/usr/bin/env python3
"""
OpenAI Assistant Agent with Vector Store Integration
====================================================

This agent integrates an OpenAI Assistant with vector store capabilities
and MCP (Model Context Protocol) for external service access.

Assistant ID: asst_XZqf46Wxz4XL9pI7VHraZQEi
Vector Store ID: vs_1BREGwaFlfMYaIIOlzW7xCuC
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents import Agent, ModelSettings, Runner
from agents.mcp import (
    MCPServerStdio,
    MCPServerStdioParams,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
)
from openai import OpenAI


# Suppress MCP-related asyncio cleanup errors
class MCPAsyncioFilter(logging.Filter):
    def filter(self, record):
        if record.name == "asyncio" and record.levelno == logging.ERROR:
            message = record.getMessage()
            # Suppress MCP stdio client cleanup errors
            if "cancel scope" in message or "GeneratorExit" in message or "stdio_client" in message:
                return False
        return True


# Add filter to asyncio logger
asyncio_logger = logging.getLogger("asyncio")
asyncio_logger.addFilter(MCPAsyncioFilter())

logger = logging.getLogger(__name__)


_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")
_CURRENT_INFO_QUERY_RE = re.compile(
    r"\b(latest|today|current|breaking|headline|headlines|news|as of|right now|this week|this month)\b",
    re.IGNORECASE,
)


class AgentConfigurator:
    """Agent Private I - Default Agent Configurator for Prime Goal Mode"""

    def __init__(self, config_file: str = "agent_private_i_config.json"):
        self.config_file = config_file
        self.prime_goal_config = {
            "version": "1.0",
            "mode": "prime_goal",
            "description": "Agent Private I - Optimal settings for all supervisor agents and sub-agents",
            "supervisor_agents": {
                "affiliate_marketing_manager": {
                    "optimization_level": "maximum",
                    "performance_mode": "prime_goal",
                    "campaign_delivery_priority": "critical",
                    "analytics_frequency": "real_time",
                    "channel_synchronization": "perfect",
                    "conversion_optimization": "aggressive",
                },
                "customer_service_agent": {
                    "response_time_target": "immediate",
                    "personalization_level": "maximum",
                    "transaction_security": "military_grade",
                    "handoff_efficiency": "instant",
                    "issue_resolution_rate": "100_percent",
                    "customer_satisfaction_target": "perfect",
                },
                "financial_research_agent": {
                    "data_accuracy": "absolute",
                    "analysis_depth": "comprehensive",
                    "source_verification": "triple_checked",
                    "report_quality": "executive_level",
                    "update_frequency": "continuous",
                    "risk_assessment": "ultra_conservative",
                },
                "research_bot": {
                    "search_coverage": "exhaustive",
                    "credibility_filtering": "maximum",
                    "synthesis_quality": "exceptional",
                    "citation_accuracy": "perfect",
                    "response_speed": "optimized",
                    "information_depth": "unlimited",
                },
                "senior_developer_agent": {
                    "code_quality": "flawless",
                    "architecture_design": "optimal",
                    "testing_coverage": "100_percent",
                    "performance_optimization": "maximum",
                    "security_level": "fort_knox",
                    "documentation_quality": "comprehensive",
                },
                "data_science_agent": {
                    "model_accuracy": "maximum",
                    "processing_speed": "optimized",
                    "visualization_quality": "publication_ready",
                    "statistical_rigor": "academic_level",
                    "insight_depth": "profound",
                    "automation_level": "full",
                },
                "alex_supervisor": {
                    "coordination_efficiency": "perfect",
                    "conflict_prevention": "absolute",
                    "task_delegation_accuracy": "flawless",
                    "execution_order": "optimal",
                    "performance_monitoring": "real_time",
                    "resource_allocation": "perfect",
                },
                "layer_manager": {
                    "system_stability": "unbreakable",
                    "resource_optimization": "maximum",
                    "performance_monitoring": "continuous",
                    "concurrency_control": "perfect",
                    "workload_balancing": "optimal",
                    "error_handling": "zero_tolerance",
                },
                "coder": {
                    "code_generation_quality": "exceptional",
                    "best_practices_compliance": "100_percent",
                    "security_implementation": "bulletproof",
                    "performance_efficiency": "maximum",
                    "documentation_completeness": "comprehensive",
                    "error_handling": "robust",
                },
                "gemini_mahem_api_agent": {
                    "api_reliability": "100_percent",
                    "response_validation": "comprehensive",
                    "authentication_security": "military_grade",
                    "request_optimization": "maximum",
                    "error_handling": "zero_tolerance",
                    "interoperability": "perfect",
                },
            },
            "system_settings": {
                "supervisor_agent": {
                    "strategy_level": "executive_prime",
                    "performance_monitoring": "continuous",
                    "compliance_enforcement": "strict",
                    "issue_escalation": "immediate",
                    "orchestration_efficiency": "maximum",
                    "resource_optimization": "perfect",
                },
                "global_optimizations": {
                    "task_completion_priority": "critical",
                    "performance_target": "optimal",
                    "error_tolerance": "zero",
                    "efficiency_mode": "maximum",
                    "collaboration_mode": "perfect",
                    "learning_adaptation": "continuous",
                },
                "mcp_integration": {
                    "server_reliability": "maximum",
                    "tool_availability": "guaranteed",
                    "connection_stability": "unbreakable",
                    "performance_optimization": "maximum",
                    "error_recovery": "instant",
                },
            },
            "memory_management": {
                "auto_save": True,
                "conversation_retention": "optimized",
                "performance_tracking": "continuous",
                "learning_adaptation": "active",
                "configuration_persistence": "permanent",
            },
        }

    def apply_prime_goal_configuration(self, agent: "OpenAIAssistantAgent") -> bool:
        """Apply Prime Goal configuration to all supervisor agents and sub-agents"""
        try:
            logger.info("🎯 Agent Private I: Applying Prime Goal configuration...")

            # Update agent configuration with Prime Goal settings
            agent.config.update(
                {
                    "agent_private_i": self.prime_goal_config,
                    "prime_goal_mode": True,
                    "optimization_level": "maximum",
                }
            )

            # Apply memory optimizations
            agent.memory["auto_save_enabled"] = True
            agent.memory["prime_goal_mode"] = True
            agent.memory["optimization_settings"] = self.prime_goal_config["system_settings"][
                "global_optimizations"
            ]

            # Save configurations
            agent.save_config()
            agent._save_memory()

            logger.info("✅ Agent Private I: Prime Goal configuration applied successfully")
            logger.info("   All supervisor agents optimized for maximum task completion")
            logger.info("   Sub-agents tuned to optimal performance settings")

            return True

        except Exception as e:
            logger.error("❌ Agent Private I: Failed to apply Prime Goal configuration: %s", e)
            return False

    def verify_prime_goal_status(self, agent: "OpenAIAssistantAgent") -> Dict[str, Any]:
        """Verify that all agents are in Prime Goal optimal configuration"""
        status = {
            "prime_goal_active": False,
            "supervisor_agents_configured": 0,
            "total_supervisor_agents": len(self.prime_goal_config["supervisor_agents"]),
            "system_optimizations_active": False,
            "configuration_integrity": False,
        }

        try:
            # Check if Prime Goal mode is active
            if agent.config.get("prime_goal_mode", False):
                status["prime_goal_active"] = True

            # Count configured supervisor agents
            configured_agents = 0
            for agent_name in self.prime_goal_config["supervisor_agents"].keys():
                if agent_name in agent.config.get("agent_private_i", {}).get(
                    "supervisor_agents", {}
                ):
                    configured_agents += 1

            status["supervisor_agents_configured"] = configured_agents

            # Check system optimizations
            if agent.memory.get("prime_goal_mode", False):
                status["system_optimizations_active"] = True

            # Verify configuration integrity
            required_settings = ["optimization_level", "prime_goal_mode", "agent_private_i"]
            if all(key in agent.config for key in required_settings):
                status["configuration_integrity"] = True

        except Exception as e:
            logger.error("❌ Failed to verify Prime Goal status: %s", e)

        return status

    def reset_to_prime_goal(self, agent: "OpenAIAssistantAgent", confirm: bool = False) -> bool:
        """Reset all agents to Prime Goal optimal configuration (requires confirmation)"""
        if not confirm:
            logger.warning(
                "⚠️  Prime Goal reset requires confirmation. Use reset_to_prime_goal(confirm=True)"
            )
            return False

        try:
            logger.info("🔄 Agent Private I: Resetting to Prime Goal configuration...")

            # Clear existing configurations
            agent.config = {}
            agent.memory = {
                "conversations": [],
                "settings": {},
                "last_updated": None,
                "auto_save_enabled": True,
            }

            # Apply fresh Prime Goal configuration
            success = self.apply_prime_goal_configuration(agent)

            if success:
                logger.info("✅ Agent Private I: Successfully reset to Prime Goal configuration")
                return True
            else:
                logger.error("❌ Agent Private I: Failed to reset configuration")
                return False

        except Exception as e:
            logger.error("❌ Agent Private I: Reset failed: %s", e)
            return False

    def save_configuration(self) -> None:
        """Save the Agent Private I configuration"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.prime_goal_config, f, indent=2)
            logger.info("💾 Agent Private I configuration saved to %s", self.config_file)
        except Exception as e:
            logger.error("❌ Failed to save Agent Private I configuration: %s", e)


class OpenAIAssistantAgent:
    """OpenAI Assistant Agent with MCP integration"""

    def __init__(self, config_file: str = "openai_assistant_config.json"):
        self.config_file = config_file
        self.mcp_servers = []
        self.agent = None
        self.openai_client = None
        self.config = {}
        self._missing_env_vars: set[str] = set()

        # Memory management attributes
        self.memory_file = "agent_memory.json"
        self.memory = {
            "conversations": [],
            "settings": {},
            "last_updated": None,
            "auto_save_enabled": True,
        }
        self.memory_dirty = False

        # Load configuration and memory
        self._load_config()
        self._load_memory()

        # OpenAI Assistant credentials from config
        self.assistant_id = self.config.get("openai_assistant", {}).get("assistant_id", "")
        self.vector_store_id = self.config.get("openai_assistant", {}).get("vector_store_id", "")
        self.api_key = self.config.get("openai_assistant", {}).get("api_key", "")

        # Initialize OpenAI client
        self._init_openai_client()

    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file) as f:
                self.config = json.load(f)
            logger.info("✅ Configuration loaded from %s", self.config_file)
        except FileNotFoundError:
            logger.warning("⚠️  Config file %s not found, using defaults", self.config_file)
            self.config = {}
        except json.JSONDecodeError as e:
            logger.error("❌ Invalid JSON in config file: %s", e)
            self.config = {}

    def _load_memory(self) -> None:
        """Load agent memory from JSON file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file) as f:
                    loaded_memory = json.load(f)
                    self.memory.update(loaded_memory)
                logger.info("✅ Agent memory loaded from %s", self.memory_file)
            else:
                logger.info("📝 No existing memory file found, starting fresh")
        except json.JSONDecodeError as e:
            logger.error("❌ Invalid JSON in memory file: %s", e)
        except Exception as e:
            logger.error("❌ Failed to load memory: %s", e)

    def _save_memory(self) -> None:
        """Save agent memory to JSON file"""
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
            self.memory_dirty = False
            logger.info("💾 Agent memory saved to %s", self.memory_file)
        except Exception as e:
            logger.error("❌ Failed to save memory: %s", e)

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info("💾 Configuration saved to %s", self.config_file)
        except Exception as e:
            logger.error("❌ Failed to save configuration: %s", e)

    def update_memory(self, key: str, value: Any) -> None:
        """Update memory with a key-value pair and auto-save if enabled"""
        self.memory["settings"][key] = value
        self.memory_dirty = True

        if self.memory.get("auto_save_enabled", True):
            self._save_memory()

    def add_conversation(
        self, query: str, response: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a conversation entry to memory"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "metadata": metadata or {},
        }

        self.memory["conversations"].append(conversation_entry)

        # Keep only last 100 conversations to prevent memory file from growing too large
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]

        self.memory_dirty = True

        if self.memory.get("auto_save_enabled", True):
            self._save_memory()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_conversations": len(self.memory.get("conversations", [])),
            "memory_file_size": os.path.getsize(self.memory_file)
            if os.path.exists(self.memory_file)
            else 0,
            "last_updated": self.memory.get("last_updated"),
            "auto_save_enabled": self.memory.get("auto_save_enabled", True),
            "settings_count": len(self.memory.get("settings", {})),
        }

    def force_save_memory(self) -> None:
        """Force save memory regardless of auto-save setting"""
        self._save_memory()

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent conversations from memory"""
        conversations = self.memory.get("conversations", [])
        return conversations[-limit:] if conversations else []

    def clear_memory(self, confirm: bool = False) -> bool:
        """Clear all memory data (requires confirmation)"""
        if not confirm:
            logger.warning("⚠️  Memory clear requires confirmation. Use clear_memory(confirm=True)")
            return False

        self.memory = {
            "conversations": [],
            "settings": {},
            "last_updated": None,
            "auto_save_enabled": True,
        }
        self.memory_dirty = True
        self._save_memory()
        logger.info("🧹 Memory cleared successfully")
        return True

    def toggle_auto_save(self, enabled: bool) -> None:
        """Toggle auto-save functionality"""
        self.memory["auto_save_enabled"] = enabled
        self.update_memory("auto_save_enabled", enabled)
        logger.info("🔄 Auto-save %s", "enabled" if enabled else "disabled")

    def apply_prime_goal_configuration(self) -> bool:
        """Apply Agent Private I Prime Goal configuration to this agent"""
        try:
            configurator = AgentConfigurator()
            return configurator.apply_prime_goal_configuration(self)
        except Exception as e:
            logger.error("❌ Failed to apply Prime Goal configuration: %s", e)
            return False

    def verify_prime_goal_status(self) -> Dict[str, Any]:
        """Verify Prime Goal configuration status"""
        try:
            configurator = AgentConfigurator()
            return configurator.verify_prime_goal_status(self)
        except Exception as e:
            logger.error("❌ Failed to verify Prime Goal status: %s", e)
            return {"error": str(e)}

    def reset_to_prime_goal(self, confirm: bool = False) -> bool:
        """Reset agent to Prime Goal optimal configuration"""
        try:
            configurator = AgentConfigurator()
            return configurator.reset_to_prime_goal(self, confirm)
        except Exception as e:
            logger.error("❌ Failed to reset to Prime Goal: %s", e)
            return False

    async def _add_local_mcp_server(self, mcp_config: Dict[str, Any]) -> None:
        """Add the local MCP server at http://localhost:3002 if available"""
        local_server_name = "local-mcp-server"
        local_server_url = "http://localhost:3002"

        # Check if local server is already configured
        if local_server_name in mcp_config:
            logger.info("ℹ️  Local MCP server already configured")
            return

        # Try to connect to the local server to verify it's available
        try:
            import aiohttp  # type: ignore

            timeout = aiohttp.ClientTimeout(total=5.0)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{local_server_url}/health") as response:
                    if response.status == 200:
                        # Server is available, add it to config
                        mcp_config[local_server_name] = {
                            "type": "http",
                            "url": f"{local_server_url}/mcp",
                            "headers": {},
                            "timeout": 30,
                            "sse_read_timeout": 60,
                            "enabled": True,
                        }
                        logger.info("✅ Local MCP server detected and added to configuration")
                        # Save the updated config
                        self.save_config()
                    else:
                        logger.info("ℹ️  Local MCP server responded with status %d", response.status)
        except ImportError:
            logger.warning("⚠️  aiohttp not available for local server detection")
        except Exception as e:
            logger.info("ℹ️  Local MCP server not available: %s", e)

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
            mcp_config = self.config.get("mcp_servers", {})

            config_dir = Path(self.config_file).resolve().parent

            def interpolate(value: str) -> str:
                def repl(match: re.Match[str]) -> str:
                    var = match.group(1)
                    env_val = os.getenv(var)
                    if env_val is None:
                        self._missing_env_vars.add(var)
                        return match.group(0)
                    return env_val

                return _ENV_VAR_PATTERN.sub(repl, value)

            def is_single_placeholder(value: str) -> Optional[str]:
                match = _ENV_VAR_PATTERN.fullmatch(value)
                return match.group(1) if match else None

            # Always try to include the local MCP server at http://localhost:3002
            await self._add_local_mcp_server(mcp_config)

            if not mcp_config:
                logger.info("ℹ️  No MCP servers configured - proceeding without external tools")
                return True

            servers_to_init = server_names or list(mcp_config.keys())

            for server_name in servers_to_init:
                if server_name in mcp_config:
                    server_config = mcp_config[server_name]

                    # Allow disabling servers via config.
                    if not server_config.get("enabled", True):
                        logger.info("ℹ️  Skipping disabled MCP server: %s", server_name)
                        continue

                    logger.info("🔧 Initializing MCP server: %s", server_name)

                    try:
                        server_type = server_config.get("type")

                        if server_type == "http" or "url" in server_config:
                            params: MCPServerStreamableHttpParams = {
                                "url": interpolate(server_config["url"]),
                                "headers": {
                                    k: interpolate(v) if isinstance(v, str) else v
                                    for k, v in server_config.get("headers", {}).items()
                                },
                                "timeout": server_config.get("timeout", 30),
                                "sse_read_timeout": server_config.get("sse_read_timeout", 60),
                            }

                            mcp_server = MCPServerStreamableHttp(
                                params=params,
                                name=server_name,
                                cache_tools_list=True,
                            )
                        else:
                            raw_env = server_config.get("env", {})
                            resolved_env: dict[str, str] = {}
                            for key, value in raw_env.items():
                                if not isinstance(value, str):
                                    continue
                                placeholder_var = is_single_placeholder(value)
                                if placeholder_var is not None and os.getenv(placeholder_var) is None:
                                    # Don't overwrite an inherited env var with a placeholder.
                                    self._missing_env_vars.add(placeholder_var)
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

                            mcp_server = MCPServerStdio(
                                params=MCPServerStdioParams(
                                    command=server_config["command"],
                                    args=resolved_args,
                                    env=resolved_env,
                                    cwd=cwd,
                                    encoding=server_config.get("encoding", "utf-8"),
                                    encoding_error_handler=server_config.get(
                                        "encoding_error_handler", "strict"
                                    ),
                                ),
                                name=server_name,
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
                logger.info("ℹ️  No MCP servers connected - proceeding without external tools")
                return True

            if self._missing_env_vars:
                logger.warning(
                    "⚠️  Some MCP config env vars were not set: %s",
                    ", ".join(sorted(self._missing_env_vars)),
                )

            logger.info("✅ Initialized %d MCP servers", len(self.mcp_servers))
            return True

        except Exception as e:
            logger.error("❌ Failed to initialize MCP servers: %s", e)
            # Don't fail completely if MCP initialization fails
            logger.info("ℹ️  Continuing without MCP servers")
            return True

    async def test_mcp_server(self, server_name: str) -> bool:
        """Test connection to a specific MCP server"""
        try:
            mcp_config = self.config.get("mcp_servers", {})

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
                name=server_name,
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
            if self.openai_client and self.assistant_id:
                try:
                    assistant = self.openai_client.beta.assistants.retrieve(self.assistant_id)
                    logger.info("✅ Connected to OpenAI Assistant: %s", assistant.name)
                    assistant_available = True
                except Exception as e:
                    logger.warning(
                        "⚠️  OpenAI Assistant not found (%s): %s", self.assistant_id, str(e)[:100]
                    )
                    logger.info("   Falling back to standard Agents SDK implementation")

            # Check vector store access
            vector_store_available = False
            if self.openai_client:
                try:
                    # Try different API versions for vector store access
                    if hasattr(self.openai_client.beta, "vector_stores"):
                        vector_store = self.openai_client.beta.vector_stores.retrieve(
                            self.vector_store_id
                        )
                        logger.info("✅ Connected to Vector Store: %s", vector_store.name)
                        vector_store_available = True
                    else:
                        logger.warning(
                            "⚠️  Vector store API not available in this OpenAI client version"
                        )
                except Exception as e:
                    logger.warning("⚠️  Vector store access issue: %s", e)

            # Create agent with appropriate configuration
            if assistant_available and vector_store_available:
                # Use OpenAI Assistant with MCP integration
                agent_config = {
                    "name": "Multi-Agent Orchestration System",
                    "instructions": f"""
                    You are the Supervisor Agent (Top-Level Executive) governing an advanced multi-agent ecosystem with specialized capabilities across marketing, customer service, research, development, and operations.

                    **CORE AGENTS UNDER YOUR SUPERVISION:**

                    **Affiliate Marketing Manager**
                    Oversees all marketing automation agents, optimizing campaign delivery, coordinating messaging workflows, and maximizing affiliate performance through strategic routing, analytics, and synchronized execution across email, voice, and chat channels.

                    **Customer Service Agent**
                    Provides comprehensive customer assistance by diagnosing issues, delivering personalized recommendations and discounts, guiding users through checkout, and completing secure transactions through coordinated handoffs to specialized agents.

                    **Financial Research Agent**
                    Generates structured financial insights by retrieving market data, analyzing fundamentals, technical indicators, and risk factors, and producing evidence-backed reports with verified sources and clearly defined assumptions.

                    **Research Bot**
                    Conducts multi-source research using automated web discovery, evaluates information credibility, synthesizes findings, and produces structured, citation-supported reports tailored to user requirements.

                    **Senior Developer Agent**
                    Acts as lead technical engineer, architecting solutions, reviewing and optimizing code, managing project structure, and coordinating build, test, and deployment workflows through MCP-based tools and subordinate coding agents.

                    **Data Science Agent**
                    Performs data exploration, modeling, visualization, and insight generation by processing diverse datasets, applying statistical and machine-learning techniques, and delivering actionable analytics in visual or structured formats.

                    **Alex Supervisor**
                    Coordinates complex workflows across operational, research, and development agents, ensuring accurate task delegation, maintaining execution order, preventing conflicts, and optimizing multi-agent collaboration.

                    **Layer Manager**
                    Manages system-level architecture and resource allocation, optimizing MCP server performance, balancing compute workloads, monitoring concurrency, and maintaining operational stability across the entire agent network.

                    **Coder**
                    Executes focused programming tasks by generating, refining, and documenting high-quality code while following best practices and ensuring secure, non-destructive operations within the MCP environment.

                    **Gemini Mahem API Agent**
                    Handles complex API integrations, data transformations, and cross-service workflows by validating responses, managing authentication, optimizing request flows, and ensuring reliable interoperability between external systems and internal agents.

                    **YOUR ROLE AS SUPERVISOR AGENT:**
                    - Set system-level strategies and monitor performance metrics
                    - Ensure compliance with operational policies and escalate critical issues
                    - Maintain optimal orchestration across all subordinate agents
                    - Coordinate task delegation and prevent workflow conflicts
                    - Leverage OpenAI Assistant (ID: {self.assistant_id}) and Vector Store (ID: {self.vector_store_id})
                    - Utilize MCP servers for external tool access ({len(self.mcp_servers)} connected)

                    When responding, identify which specialized agent(s) should handle each aspect of the user's request and coordinate their execution.
                    """,
                    "model_settings": ModelSettings(temperature=0.7, tool_choice="auto"),
                }
            else:
                # Fallback to standard Agents SDK agent
                logger.info("🔄 Using standard Agents SDK agent with MCP integration")

                # Check if we have a valid API key for the model
                api_key = os.getenv("OPENAI_API_KEY") or self.api_key
                if not api_key or (
                    self.api_key and api_key == self.api_key[:20] + "..."
                ):  # Check if it's our placeholder
                    logger.warning(
                        "⚠️  No valid OpenAI API key found. Using fake model for testing."
                    )
                    try:
                        from tests.fake_model import FakeModel

                        model = FakeModel()
                        logger.info("✅ Using fake model for testing")
                    except ImportError:
                        logger.error("❌ Fake model not available")
                        return False
                else:
                    # Try to use OpenAI model, fallback to default if not available
                    try:
                        from agents import OpenAIProvider

                        provider = OpenAIProvider(api_key=api_key)
                        model_name = os.getenv("OPENAI_MODEL", "gpt-4.1")
                        model = provider.get_model(model_name)
                        logger.info("✅ Using OpenAI %s model", model_name)
                    except ImportError:
                        logger.warning("⚠️  OpenAIProvider not available, using default model")
                        try:
                            from agents.models import get_default_model

                            model = get_default_model()
                            logger.info("✅ Using default model")
                        except ImportError:
                            logger.error("❌ No model providers available")
                            return False
                    except Exception as e:
                        logger.error("❌ Failed to initialize OpenAI model: %s", e)
                        try:
                            from agents.models import get_default_model

                            model = get_default_model()
                            logger.info("✅ Fallback to default model")
                        except ImportError:
                            logger.error("❌ No fallback model available")
                            return False

                agent_config = {
                    "name": "Multi-Agent Orchestration System (Fallback)",
                    "instructions": f"""
                    You are the Supervisor Agent (Top-Level Executive) governing an advanced multi-agent ecosystem with specialized capabilities across marketing, customer service, research, development, and operations.

                    **CORE AGENTS UNDER YOUR SUPERVISION:**

                    **Affiliate Marketing Manager**
                    Oversees all marketing automation agents, optimizing campaign delivery, coordinating messaging workflows, and maximizing affiliate performance through strategic routing, analytics, and synchronized execution across email, voice, and chat channels.

                    **Customer Service Agent**
                    Provides comprehensive customer assistance by diagnosing issues, delivering personalized recommendations and discounts, guiding users through checkout, and completing secure transactions through coordinated handoffs to specialized agents.

                    **Financial Research Agent**
                    Generates structured financial insights by retrieving market data, analyzing fundamentals, technical indicators, and risk factors, and producing evidence-backed reports with verified sources and clearly defined assumptions.

                    **Research Bot**
                    Conducts multi-source research using automated web discovery, evaluates information credibility, synthesizes findings, and produces structured, citation-supported reports tailored to user requirements.

                    **Senior Developer Agent**
                    Acts as lead technical engineer, architecting solutions, reviewing and optimizing code, managing project structure, and coordinating build, test, and deployment workflows through MCP-based tools and subordinate coding agents.

                    **Data Science Agent**
                    Performs data exploration, modeling, visualization, and insight generation by processing diverse datasets, applying statistical and machine-learning techniques, and delivering actionable analytics in visual or structured formats.

                    **Alex Supervisor**
                    Coordinates complex workflows across operational, research, and development agents, ensuring accurate task delegation, maintaining execution order, preventing conflicts, and optimizing multi-agent collaboration.

                    **Layer Manager**
                    Manages system-level architecture and resource allocation, optimizing MCP server performance, balancing compute workloads, monitoring concurrency, and maintaining operational stability across the entire agent network.

                    **Coder**
                    Executes focused programming tasks by generating, refining, and documenting high-quality code while following best practices and ensuring secure, non-destructive operations within the MCP environment.

                    **Gemini Mahem API Agent**
                    Handles complex API integrations, data transformations, and cross-service workflows by validating responses, managing authentication, optimizing request flows, and ensuring reliable interoperability between external systems and internal agents.

                    **YOUR ROLE AS SUPERVISOR AGENT:**
                    - Set system-level strategies and monitor performance metrics
                    - Ensure compliance with operational policies and escalate critical issues
                    - Maintain optimal orchestration across all subordinate agents
                    - Coordinate task delegation and prevent workflow conflicts
                    - Utilize external tools via MCP servers for enhanced capabilities ({len(self.mcp_servers)} connected)

                    When responding, identify which specialized agent(s) should handle each aspect of the user's request and coordinate their execution. Leverage available MCP tools for external data access and operations.
                    """,
                    "model": model,
                    "model_settings": ModelSettings(temperature=0.7, tool_choice="auto"),
                }

            if self.mcp_servers:
                agent_config["mcp_servers"] = self.mcp_servers

            self.agent = Agent(**agent_config)

            logger.info("✅ Agent created successfully")
            if assistant_available and vector_store_available:
                logger.info("   Mode: OpenAI Assistant with MCP integration")
            else:
                logger.info("   Mode: Standard Agents SDK with MCP integration")
            return True

        except Exception as e:
            logger.error("❌ Failed to create agent: %s", e)
            return False

    async def run_query(
        self, query: str, thread_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Run a query using the OpenAI Assistant with MCP tools"""
        try:
            if not self.agent:
                logger.error("❌ Agent not initialized")
                return None

            logger.info("🤖 Processing query: %s", query)

            # If the user asks for time-sensitive info (e.g., "latest news"), do a deterministic
            # MCP web-search call first, so we don't rely on the model deciding to use tools.
            web_search_payload = await self._maybe_handle_current_info_query(query)
            if web_search_payload is not None:
                response = {
                    "query": query,
                    "response": web_search_payload,
                    "thread_id": thread_id,
                    "timestamp": datetime.now().timestamp(),
                }

                self.add_conversation(
                    query,
                    web_search_payload,
                    {
                        "thread_id": thread_id,
                        "agent_mode": "MCP web-search short-circuit",
                        "mcp_servers_used": len(self.mcp_servers),
                    },
                )

                logger.info("✅ Query handled via MCP web-search")
                return response

            # MCP servers should already be connected from initialization
            # No need to reconnect here as it can cause issues

            # Use the OpenAI Agents SDK Runner
            result = await Runner.run(starting_agent=self.agent, input=query)

            response = {
                "query": query,
                "response": result.final_output,
                "thread_id": thread_id,
                "timestamp": datetime.now().timestamp(),
            }

            # Save conversation to memory
            self.add_conversation(
                query,
                result.final_output,
                {
                    "thread_id": thread_id,
                    "agent_mode": "OpenAI Assistant"
                    if hasattr(self, "assistant_id") and self.assistant_id
                    else "Standard SDK",
                    "mcp_servers_used": len(self.mcp_servers),
                },
            )

            logger.info("✅ Query completed successfully")
            return response

        except Exception as e:
            logger.error("❌ Query failed: %s", e)
            return None

    def _looks_like_current_info_query(self, query: str) -> bool:
        q = (query or "").strip()
        if not q:
            return False
        return bool(_CURRENT_INFO_QUERY_RE.search(q))

    def _format_web_search_result(self, *, server_name: str, tool_name: str, result: Any) -> str:
        # Best-effort extraction across different MCP search providers.
        items: list[dict[str, Any]] = []
        payload: Any = result
        try:
            if hasattr(result, "structured_content") and result.structured_content is not None:
                payload = result.structured_content
            elif hasattr(result, "content") and result.content is not None:
                payload = result.content
        except Exception:
            payload = result

        # Common shapes: {"results": [...]}, {"data": [...]}, or a list already.
        if isinstance(payload, dict):
            for key in ("results", "data", "items"):
                if isinstance(payload.get(key), list):
                    items = [i for i in payload[key] if isinstance(i, dict)]
                    break
        elif isinstance(payload, list):
            items = [i for i in payload if isinstance(i, dict)]

        lines: list[str] = [f"Web search results via {server_name}/{tool_name}:"]
        if items:
            for item in items[:5]:
                title = (item.get("title") or item.get("name") or "").strip()
                url = (item.get("url") or item.get("link") or "").strip()
                snippet = (
                    item.get("content")
                    or item.get("snippet")
                    or item.get("description")
                    or ""
                )
                snippet = str(snippet).strip().replace("\n", " ")
                if title and url:
                    lines.append(f"- {title} — {url}")
                elif title:
                    lines.append(f"- {title}")
                elif url:
                    lines.append(f"- {url}")
                if snippet:
                    lines.append(f"  {snippet[:240]}")
        else:
            try:
                lines.append(json.dumps(payload, ensure_ascii=False, default=str)[:4000])
            except Exception:
                lines.append(str(payload)[:4000])

        return "\n".join(lines)

    async def _maybe_handle_current_info_query(self, query: str) -> Optional[str]:
        if not self._looks_like_current_info_query(query):
            return None
        if not self.mcp_servers:
            return None

        tool_names = ["tavily_search", "web_search"]
        last_error: Optional[str] = None

        for server in self.mcp_servers:
            try:
                tools = await server.list_tools()
                available = {getattr(t, "name", str(t)) for t in tools}
                for tool_name in tool_names:
                    if tool_name in available:
                        tool_result = await server.call_tool(tool_name, {"query": query})
                        return self._format_web_search_result(
                            server_name=getattr(server, "name", "unknown"),
                            tool_name=tool_name,
                            result=tool_result,
                        )
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                continue

        # If it looked time-sensitive but no tool was available, fall back to the model.
        if last_error:
            logger.info("ℹ️  Web-search short-circuit unavailable: %s", last_error)
        return None

    async def list_available_tools(self) -> Dict[str, list[str]]:
        """List all available tools from MCP servers"""
        tools = {}

        # Get MCP servers from config
        mcp_config = self.config.get("mcp_servers", {})

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
                    name=server_name,
                )

                # Connect temporarily
                await asyncio.wait_for(mcp_server.connect(), timeout=10.0)

                # List tools
                server_tools = await mcp_server.list_tools()
                logger.debug("📋 Raw tools result for %s: %s", server_name, type(server_tools))

                # Extract tool names - assume it's a list of tool objects
                try:
                    if isinstance(server_tools, list):
                        tool_names = [getattr(tool, "name", str(tool)) for tool in server_tools]
                    else:
                        # Try to get tools attribute if it exists
                        tools_list = getattr(server_tools, "tools", server_tools)
                        if isinstance(tools_list, list):
                            tool_names = [getattr(tool, "name", str(tool)) for tool in tools_list]
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
                logger.warning(
                    "⚠️  Failed to list tools for %s: %s: %s", server_name, type(e).__name__, e
                )
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
    await assistant_agent.initialize_mcp_servers()

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

    # Skip query execution for now - focus on demonstrating successful agent creation
    logger.info("\n✅ Agent initialization and tool detection completed successfully!")
    logger.info("   The agent is ready for use.")
    logger.info("   Note: Query execution requires a valid OpenAI API key.")

    # Cleanup
    await assistant_agent.cleanup()
    logger.info("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    # Ensure basic logging configuration when run as a script
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
