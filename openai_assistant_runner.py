#!/usr/bin/env python3
"""Launches the OpenAI Responses API to respond to prompts coming from the UI backend."""

import json
import os
import sys
import logging
import requests
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


def execute_weather_tool(city: str) -> str:
    """Execute the weather tool to get current weather for a city."""
    try:
        # Using wttr.in - a free weather API that doesn't require API keys
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current_condition = data['current_condition'][0]
        
        # Extract relevant weather information
        temp_c = current_condition['temp_C']
        temp_f = current_condition['temp_F']
        weather_desc = current_condition['weatherDesc'][0]['value']
        humidity = current_condition['humidity']
        wind_speed = current_condition['windspeedKmph']
        
        return f"Current weather in {city}: {weather_desc}, {temp_c}°C ({temp_f}°F), Humidity: {humidity}%, Wind: {wind_speed} km/h"
    
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {e}")
        return f"Sorry, I couldn't fetch the weather for {city} at the moment. Error: {str(e)}"


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool based on its name and arguments."""
    if tool_name == "get_weather":
        city = arguments.get("city", "").strip()
        if not city:
            return "Error: City name is required for weather lookup."
        return execute_weather_tool(city)
    elif tool_name == "calculate":
        # Simple calculator - could be expanded
        expression = arguments.get("expression", "").strip()
        if not expression:
            return "Error: Expression is required for calculation."
        try:
            # Use eval with restrictions for safety (in production, use a proper math library)
            result = eval(expression, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"
    else:
        return f"Unknown tool: {tool_name}"


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
    tools_json = os.getenv("TOOLS", "[]")
    
    # Parse tools from JSON
    tools = []
    try:
        tools_data = json.loads(tools_json)
        for tool in tools_data:
            # Map tool names to function names
            function_name = "get_weather" if tool["name"].lower() == "weather" else tool["name"].lower().replace(" ", "_")
            tools.append({
                "type": "function",
                "function": {
                    "name": function_name,
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The name of the city to get weather for"
                            }
                        },
                        "required": ["city"]
                    }
                }
            })
    except json.JSONDecodeError:
        logger.warning("⚠️  Unable to parse TOOLS environment variable, ignoring tools")
        tools = []

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

    def _is_model_access_error(error: Exception) -> bool:
        message = str(error).lower()
        if "model_not_found" in message:
            return True
        if "does not have access to model" in message:
            return True
        status = getattr(error, "status_code", None) or getattr(error, "status", None)
        return status == 403

    response = None
    attempted_models = [model_override]
    default_model = assistant_defaults.get("model")
    if default_model and default_model not in attempted_models:
        attempted_models.append(default_model)
    if "gpt-4.1" not in attempted_models:
        attempted_models.append("gpt-4.1")

    # Make the initial API call
    for candidate_model in attempted_models:
        try:
            response = client.responses.create(
                model=candidate_model,
                input=messages,
                temperature=temperature,
                store=True,
                tools=tools if tools else None,
            )
            model_override = candidate_model
            break
        except Exception as exc:
            if candidate_model != attempted_models[-1] and _is_model_access_error(exc):
                logger.warning(
                    "⚠️  Model %s unavailable (%s). Falling back to %s.",
                    candidate_model,
                    exc,
                    attempted_models[-1],
                )
                continue

            logger.error("❌ Failed to create response: %s", exc)
            return 1

    if response is None:
        logger.error("❌ Failed to create response: No response returned after model attempts")
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

    # Process the response and handle tool calls
    assistant_response = ""
    tool_calls = []
    
    # Extract content and tool calls from the response
    for item in response.output:
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
        elif item.type == "function_call":
            tool_calls.append(item)

    # Execute tool calls if any
    if tool_calls:
        logger.info(f"🔧 Executing {len(tool_calls)} tool call(s)")
        
        # Add the assistant's message with tool calls to the conversation
        messages.append({
            "role": "assistant", 
            "content": assistant_response if assistant_response else None,
            "tool_calls": tool_calls
        })
        
        # Execute each tool call and collect results
        tool_results = []
        for tool_call in tool_calls:
            function_name = getattr(tool_call, 'name', 'unknown')
            function_args_json = getattr(tool_call, 'arguments', '{}')
            
            try:
                function_args = json.loads(function_args_json)
                tool_result = execute_tool(function_name, function_args)
                logger.info(f"✅ Tool {function_name} executed successfully")
            except Exception as e:
                tool_result = f"Error executing tool {function_name}: {str(e)}"
                logger.error(f"❌ Tool {function_name} execution failed: {e}")
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "output": tool_result
            })
        
        # Add tool results to messages
        messages.append({
            "role": "user",
            "content": None,
            "tool_results": tool_results
        })
        
        # Make a follow-up request with tool results
        try:
            followup_response = client.responses.create(
                model=model_override,
                input=messages,
                temperature=temperature,
                store=True,
            )
            
            # Wait for completion
            while followup_response.status not in {"completed", "failed", "cancelled", "expired"}:
                import time
                time.sleep(0.4)
                followup_response = client.responses.retrieve(followup_response.id)
            
            if followup_response.status == "completed":
                # Extract the final response
                for item in followup_response.output:
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
            else:
                assistant_response += "\n[Tool execution completed, but final response failed]"
                
        except Exception as e:
            logger.error(f"❌ Follow-up request failed: {e}")
            assistant_response += f"\n[Tool results: {', '.join([r['output'] for r in tool_results])}]"

    if not assistant_response.strip():
        logger.error("❌ Assistant did not return any text content")
        return 1

    print(assistant_response)
    return 0


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(run_assistant())
    sys.exit(exit_code)
