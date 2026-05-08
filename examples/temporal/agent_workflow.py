#!/usr/bin/env python3
"""
Example of integrating OpenAI Agents SDK with Temporal workflows.

This example demonstrates how to orchestrate agent runs using Temporal's
workflow engine for reliable, durable agent execution.
"""

import asyncio
import logging
from datetime import timedelta
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

logger = logging.getLogger(__name__)

# Add the src directory to the path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents import Agent, Runner
from tests.fake_model import FakeModel


@workflow.defn
class AgentWorkflow:
    """A Temporal workflow that runs an OpenAI Agent."""

    @workflow.run
    async def run(self, prompt: str) -> str:
        """Execute an agent workflow with the given prompt."""
        # Create agent with fake model for demo
        agent = Agent(
            name="Temporal Agent",
            instructions="You are a helpful assistant running in a Temporal workflow.",
            model=FakeModel(),
        )

        # Run the agent
        result = await Runner.run(agent, prompt)

        return result.final_output


async def main():
    """Run the Temporal worker and execute a workflow."""
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Start worker
    async with Worker(
        client,
        task_queue="agent-task-queue",
        workflows=[AgentWorkflow],
    ):
        logger.info("Worker started. Press Ctrl+C to stop.")

        # Execute a workflow
        result = await client.execute_workflow(
            AgentWorkflow.run,
            "Hello from Temporal! Can you tell me about workflow orchestration?",
            id="agent-workflow-1",
            task_queue="agent-task-queue",
        )

        logger.info("Workflow result: %s", result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())