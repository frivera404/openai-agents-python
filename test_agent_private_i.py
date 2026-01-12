#!/usr/bin/env python3
"""
Test script for Agent Private I - Prime Goal Configuration
==========================================================

This script demonstrates the Agent Private I configurator that sets all
supervisor agents to Prime Goal mode for optimal task completion.
"""

import asyncio
import logging

from openai_assistant_agent import AgentConfigurator, OpenAIAssistantAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_agent_private_i():
    """Test Agent Private I Prime Goal configuration"""
    logger.info("🎯 Testing Agent Private I - Prime Goal Configuration")
    logger.info("=" * 60)

    # Initialize agent
    agent = OpenAIAssistantAgent()
    configurator = AgentConfigurator()

    # Check initial status
    logger.info("📊 Initial Prime Goal status:")
    initial_status = configurator.verify_prime_goal_status(agent)
    logger.info("   Prime Goal Active: %s", initial_status["prime_goal_active"])
    logger.info(
        "   Supervisor Agents Configured: %d/%d",
        initial_status["supervisor_agents_configured"],
        initial_status["total_supervisor_agents"],
    )

    # Apply Prime Goal configuration
    logger.info("\n⚙️  Applying Prime Goal configuration...")
    success = agent.apply_prime_goal_configuration()

    if success:
        logger.info("✅ Prime Goal configuration applied successfully!")

        # Verify configuration
        logger.info("\n🔍 Verifying configuration...")
        status = agent.verify_prime_goal_status()

        logger.info("📊 Post-configuration status:")
        logger.info("   Prime Goal Active: %s", status["prime_goal_active"])
        logger.info(
            "   Supervisor Agents Configured: %d/%d",
            status["supervisor_agents_configured"],
            status["total_supervisor_agents"],
        )
        logger.info("   System Optimizations Active: %s", status["system_optimizations_active"])
        logger.info("   Configuration Integrity: %s", status["configuration_integrity"])

        # Show some configuration details
        logger.info("\n🔧 Sample optimized settings:")
        prime_config = agent.config.get("agent_private_i", {})
        if prime_config:
            supervisor_agents = prime_config.get("supervisor_agents", {})
            for agent_name, settings in list(supervisor_agents.items())[:3]:  # Show first 3
                logger.info(
                    "   %s: optimization_level=%s",
                    agent_name.replace("_", " ").title(),
                    settings.get("optimization_level", "unknown"),
                )
            if len(supervisor_agents) > 3:
                logger.info("   ... and %d more agents", len(supervisor_agents) - 3)

        # Test memory integration
        logger.info("\n🧠 Memory integration:")
        memory_stats = agent.get_memory_stats()
        logger.info("   Auto-save enabled: %s", memory_stats["auto_save_enabled"])
        logger.info("   Prime Goal mode in memory: %s", agent.memory.get("prime_goal_mode", False))

    else:
        logger.error("❌ Failed to apply Prime Goal configuration")


async def test_configuration_reset():
    """Test configuration reset functionality"""
    logger.info("\n🔄 Testing Configuration Reset")
    logger.info("=" * 40)

    agent = OpenAIAssistantAgent()

    # First apply configuration
    agent.apply_prime_goal_configuration()

    # Verify it's applied
    status_before = agent.verify_prime_goal_status()
    logger.info("Before reset - Prime Goal active: %s", status_before["prime_goal_active"])

    # Reset to Prime Goal (with confirmation)
    logger.info("Resetting to fresh Prime Goal configuration...")
    reset_success = agent.reset_to_prime_goal(confirm=True)

    if reset_success:
        logger.info("✅ Reset successful!")
        status_after = agent.verify_prime_goal_status()
        logger.info("After reset - Prime Goal active: %s", status_after["prime_goal_active"])
    else:
        logger.error("❌ Reset failed")


async def demonstrate_supervisor_agents():
    """Demonstrate the configured supervisor agents"""
    logger.info("\n👥 Supervisor Agents in Prime Goal Mode")
    logger.info("=" * 45)

    configurator = AgentConfigurator()

    logger.info("All supervisor agents configured for maximum performance:")
    for agent_name, settings in configurator.prime_goal_config["supervisor_agents"].items():
        display_name = agent_name.replace("_", " ").title()
        opt_level = settings.get("optimization_level", "unknown")
        logger.info("   • %s: %s optimization", display_name, opt_level)

    logger.info("\n🎯 System-wide optimizations active:")
    global_opts = configurator.prime_goal_config["system_settings"]["global_optimizations"]
    for opt_name, level in global_opts.items():
        display_opt = opt_name.replace("_", " ").title()
        logger.info("   • %s: %s", display_opt, level)


async def main():
    """Main test function"""
    logger.info("🚀 Agent Private I - Prime Goal Configuration Test")
    logger.info("=" * 60)

    try:
        # Test Agent Private I functionality
        await test_agent_private_i()

        # Test configuration reset
        await test_configuration_reset()

        # Demonstrate supervisor agents
        await demonstrate_supervisor_agents()

        logger.info("\n✅ All Agent Private I tests completed successfully!")
        logger.info("   All supervisor agents are now optimized for Prime Goal task completion.")

    except Exception as e:
        logger.error("❌ Test failed: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
