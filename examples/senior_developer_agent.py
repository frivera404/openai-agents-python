#!/usr/bin/env python3
"""
Senior Developer Agent Example

This example demonstrates an agent that acts as a senior developer,
using OpenAI's Assistants API with a vector store for knowledge retrieval.
The agent can consult the assistant for code-related advice and use MCP tools for filesystem operations.
"""

import asyncio
import os
import logging
from openai import OpenAI

from agents import Agent, Runner, gen_trace_id, trace, function_tool
from agents.mcp import MCPServerStreamableHttp

logger = logging.getLogger(__name__)


# OpenAI client setup
client = OpenAI()

ASSISTANT_ID = "asst_70Xrb6BnK0CtVx3qm89J6nEQ"
VECTOR_STORE_ID = "vs_1BREGwaFlfMYaIIOlzW7xCuC"


@function_tool
async def consult_assistant(query: str) -> str:
    """
    Consult the senior developer assistant for advice.
    This creates a thread, adds the query, runs the assistant, and retrieves the response.
    """
    try:
        # Create a thread
        thread = client.beta.threads.create()

        # Add the query as a message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the run to complete
        while run.status != "completed":
            await asyncio.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run.status == "failed":
                return f"Assistant run failed: {run.last_error}"

        # Retrieve the messages
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value

        return response
    except Exception as e:
        return f"Error consulting assistant: {str(e)}"


async def main():
    # MCP server for filesystem access
    mcp_server = MCPServerStreamableHttp(
        name="Docker Filesystem Server",
        params={
            "url": "http://mcp-filesystem:8000/mcp",
        },
    )
    await mcp_server.connect()

    # Agent setup
    agent = Agent(
        name="Senior Developer Agent",
        instructions="""
        You are a senior software developer with extensive experience in Python, web development, and system architecture.
        You have access to a knowledge base via the assistant tool and can use filesystem tools to read/write code.

        When faced with a task:
        1. Analyze the requirements carefully
        2. Consult the assistant for relevant knowledge or best practices if needed
        3. Use filesystem tools to examine existing code or create new files
        4. Provide clear, well-structured code with comments
        5. Explain your reasoning and any trade-offs

        Always write production-ready, maintainable code following best practices.
        """,
        mcp_servers=[mcp_server],
        tools=[consult_assistant],  # Add the assistant consultation tool
    )

    # Generate trace ID
    trace_id = gen_trace_id()

    with trace(workflow_name="Senior Developer Agent Example", trace_id=trace_id):
        logger.info("View trace: https://platform.openai.com/traces/trace?trace_id=%s\n", trace_id)

        # Example tasks
        tasks = [
            "Create a Python function to parse JSON configuration files with error handling",
            "Design a simple REST API endpoint for user authentication",
            "Refactor the existing integration_example.py to use async/await properly",
        ]

        for task in tasks:
            logger.info("\n=== Task: %s ===", task)
            result = await Runner.run(starting_agent=agent, input=task)
            logger.info("%s", result.final_output)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())