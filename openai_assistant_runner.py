#!/usr/bin/env python3
"""Launches the OpenAI Responses API to respond to prompts coming from the UI backend."""

import json
import os
import sys
import logging
from pathlib import Path

from openai import OpenAI

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).with_name("openai_assistant_config.json")


def load_config() -> dict[str, any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError:
        logger.warning("⚠️  Unable to parse %s, ignoring defaults", CONFIG_PATH)
        return {}


async def run_assistant() -> int:
    config = load_config()
    assistant_defaults = config.get("openai_assistant", {})

    api_key = os.getenv("OPENAI_API_KEY") or assistant_defaults.get("api_key")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY is required")
        return 1

    prompt = os.getenv("PROMPT")
    if not prompt:
        logger.error("❌ PROMPT is required")
        return 1

    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    instructions = os.getenv("AGENT_INSTRUCTIONS", "").strip()
    override_system = os.getenv("SYSTEM_INSTRUCTION", "").strip()
    thread_description = os.getenv("AGENT_ID", "assistant")
    model_override = os.getenv("MODEL") or assistant_defaults.get("model", "gpt-4.1")

    if thread_description == 'web-research':
        from web_research_agent import run_web_research_workflow
        result = await run_web_research_workflow(prompt)
        print(result['output_text'])
        return 0

    client = OpenAI(api_key=api_key)

    system_content = override_system or instructions
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.responses.create(
            model=model_override,
            input=messages,
            temperature=temperature,
            store=True,
        )
    except Exception as exc:
        logger.error("❌ Failed to create response: %s", exc)
        return 1

    # Wait for completion
    while response.status not in {"completed", "failed", "cancelled", "expired"}:
        import time
        time.sleep(0.4)
        response = client.responses.retrieve(response.id)

    if response.status != "completed":
        error = getattr(response, "error", None)
        message = getattr(error, "message", "Unknown error") if error else "Response did not finish successfully"
        logger.error("❌ Response %s: %s", response.status, message)
        return 1

    # Check for refusal if available
    try:
        if response.refusal:
            logger.error("❌ Response refused: %s", response.refusal)
            return 1
    except AttributeError:
        pass  # Refusal not available in this version

    # Extract the assistant response
    output = response.output
    if not output:
        logger.error("❌ Response did not return any output")
        return 1

    assistant_response = ""
    for item in output:
        if item.type == "message":
            content = item.content
            if isinstance(content, list):
                for c in content:
                    c_type = getattr(c, 'type', None)
                    if c_type in ("output_text", "text"):
                        text_obj = getattr(c, 'text', None)
                        if isinstance(text_obj, str):
                            assistant_response += text_obj
                        elif isinstance(text_obj, dict):
                            text_value = text_obj.get("value") or text_obj.get("text")
                            if text_value:
                                assistant_response += str(text_value)

    if not assistant_response.strip():
        logger.error("❌ Assistant did not return any text content")
        return 1

    print(assistant_response)
    return 0


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(run_assistant())
    sys.exit(exit_code)
