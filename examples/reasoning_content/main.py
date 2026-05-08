"""
Example demonstrating how to use the reasoning content feature with models that support it.

Some models, like gpt-5, provide a reasoning_content field in addition to the regular content.
This example shows how to access and use this reasoning content from both streaming and non-streaming responses.

To run this example, you need to:
1. Set your OPENAI_API_KEY environment variable
2. Use a model that supports reasoning content (e.g., gpt-5)
"""

import asyncio
import os
import logging
from typing import Any, cast

from agents import ModelSettings
from agents.models.interface import ModelTracing
from agents.models.openai_provider import OpenAIProvider
from openai.types.responses import ResponseOutputRefusal, ResponseOutputText
from openai.types.shared.reasoning import Reasoning

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("EXAMPLE_MODEL_NAME") or "gpt-5"


async def stream_with_reasoning_content():
    """
    Example of streaming a response from a model that provides reasoning content.
    The reasoning content will be emitted as separate events.
    """
    provider = OpenAIProvider()
    model = provider.get_model(MODEL_NAME)

    logger.info("\n=== Streaming Example ===")
    logger.info("Prompt: Write a haiku about recursion in programming")

    reasoning_content = ""
    regular_content = ""

    output_text_already_started = False
    async for event in model.stream_response(
        system_instructions="You are a helpful assistant that writes creative content.",
        input="Write a haiku about recursion in programming",
        model_settings=ModelSettings(reasoning=Reasoning(effort="medium", summary="detailed")),
        tools=[],
        output_schema=None,
        handoffs=[],
        tracing=ModelTracing.DISABLED,
        previous_response_id=None,
        conversation_id=None,
        prompt=None,
    ):
        if event.type == "response.reasoning_summary_text.delta":
            # Yellow for reasoning content
            logger.info("%s", event.delta)
            reasoning_content += event.delta
        elif event.type == "response.output_text.delta":
            if not output_text_already_started:
                logger.info("\n")
                output_text_already_started = True
            # Green for regular content
            logger.info("%s", event.delta)
            regular_content += event.delta
    logger.info("\n")


async def get_response_with_reasoning_content():
    """
    Example of getting a complete response from a model that provides reasoning content.
    The reasoning content will be available as a separate item in the response.
    """
    provider = OpenAIProvider()
    model = provider.get_model(MODEL_NAME)

    logger.info("\n=== Non-streaming Example ===")
    logger.info("Prompt: Explain the concept of recursion in programming")

    response = await model.get_response(
        system_instructions="You are a helpful assistant that explains technical concepts clearly.",
        input="Explain the concept of recursion in programming",
        model_settings=ModelSettings(reasoning=Reasoning(effort="medium", summary="detailed")),
        tools=[],
        output_schema=None,
        handoffs=[],
        tracing=ModelTracing.DISABLED,
        previous_response_id=None,
        conversation_id=None,
        prompt=None,
    )

    # Extract reasoning content and regular content from the response
    reasoning_content = None
    regular_content = None

    for item in response.output:
        if hasattr(item, "type") and item.type == "reasoning":
            reasoning_content = item.summary[0].text
        elif hasattr(item, "type") and item.type == "message":
            if item.content and len(item.content) > 0:
                content_item = item.content[0]
                if isinstance(content_item, ResponseOutputText):
                    regular_content = content_item.text
                elif isinstance(content_item, ResponseOutputRefusal):
                    refusal_item = cast(Any, content_item)
                    regular_content = refusal_item.refusal

    logger.info("\n\n### Reasoning Content:")
    logger.info("%s", reasoning_content or "No reasoning content provided")
    logger.info("\n\n### Regular Content:")
    logger.info("%s", regular_content or "No regular content provided")
    logger.info("\n")


async def main():
    try:
        await stream_with_reasoning_content()
        await get_response_with_reasoning_content()
    except Exception as e:
        logger.error("Error: %s", e)
        logger.info("\nNote: This example requires a model that supports reasoning content.")
        logger.info("You may need to use a specific model like gpt-5 or similar.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
