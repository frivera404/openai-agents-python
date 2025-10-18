import base64
import json
from types import SimpleNamespace
from typing import Any

import pytest

from agents import Agent, RunContextWrapper, ToolInputGuardrailData, ToolOutputGuardrailData, Usage
from agents.tool_context import ToolContext
from examples.basic import (
    agent_lifecycle_example,
    dynamic_system_prompt,
    local_file,
    local_image,
    prompt_template,
    stream_function_call_args,
    stream_items,
    tool_guardrails,
    tools,
    usage_tracking,
)


async def _invoke_tool(tool: Any, arguments: dict[str, Any]) -> Any:
    ctx = ToolContext(
        context=None,
        usage=Usage(),
        tool_name=tool.name,
        tool_call_id="call_123",
        tool_arguments=json.dumps(arguments),
    )
    return await tool.on_invoke_tool(ctx, json.dumps(arguments))


@pytest.mark.asyncio
async def test_tools_get_weather_returns_weather_model() -> None:
    result = await _invoke_tool(tools.get_weather, {"city": "Tokyo"})
    assert result.city == "Tokyo"
    assert result.temperature_range
    assert result.conditions


@pytest.mark.asyncio
async def test_agent_lifecycle_random_number_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent_lifecycle_example.random, "randint", lambda _a, _b: 7)
    result = await _invoke_tool(agent_lifecycle_example.random_number, {"max": 10})
    assert result == 7


@pytest.mark.asyncio
async def test_agent_lifecycle_multiply_by_two_tool() -> None:
    result = await _invoke_tool(agent_lifecycle_example.multiply_by_two, {"x": 4})
    assert result == 8


def test_dynamic_system_prompt_custom_instructions() -> None:
    agent = Agent(name="Test", instructions="placeholder")
    context = RunContextWrapper(context=dynamic_system_prompt.CustomContext(style="haiku"))
    message = dynamic_system_prompt.custom_instructions(context, agent)
    assert message == "Only respond in haikus."

    context = RunContextWrapper(context=dynamic_system_prompt.CustomContext(style="pirate"))
    message = dynamic_system_prompt.custom_instructions(context, agent)
    assert message == "Respond as a pirate."

    context = RunContextWrapper(context=dynamic_system_prompt.CustomContext(style="robot"))
    message = dynamic_system_prompt.custom_instructions(context, agent)
    assert message == "Respond as a robot and say 'beep boop' a lot."


@pytest.mark.asyncio
async def test_prompt_template_get_dynamic_prompt_uses_context() -> None:
    dynamic_context = prompt_template.DynamicContext("pmpt_test")
    dynamic_context.poem_style = "haiku"
    data = SimpleNamespace(context=SimpleNamespace(context=dynamic_context))

    result = await prompt_template._get_dynamic_prompt(data)

    assert result["id"] == "pmpt_test"
    assert result["variables"]["poem_style"] == "haiku"


@pytest.mark.asyncio
async def test_prompt_template_dynamic_prompt_invokes_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_run(agent: Agent, message: str, *, context: Any) -> SimpleNamespace:
        captured["agent"] = agent
        captured["message"] = message
        captured["context"] = context
        return SimpleNamespace(final_output="result")

    monkeypatch.setattr(prompt_template.Runner, "run", fake_run)
    monkeypatch.setattr(prompt_template.random, "choice", lambda options: "haiku")

    await prompt_template.dynamic_prompt("pmpt_test")

    assert captured["message"] == "Tell me about recursion in programming."
    assert isinstance(captured["agent"], Agent)
    assert captured["context"].prompt_id == "pmpt_test"
    assert captured["context"].poem_style == "haiku"


@pytest.mark.asyncio
async def test_prompt_template_static_prompt_invokes_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_run(agent: Agent, message: str) -> SimpleNamespace:
        captured["agent"] = agent
        captured["message"] = message
        return SimpleNamespace(final_output="result")

    monkeypatch.setattr(prompt_template.Runner, "run", fake_run)

    await prompt_template.static_prompt("pmpt_test")

    assert captured["message"] == "Tell me about recursion in programming."
    assert captured["agent"].prompt == {
        "id": "pmpt_test",
        "version": "1",
        "variables": {"poem_style": "limerick"},
    }


def test_local_file_to_base64_roundtrip() -> None:
    encoded = local_file.file_to_base64(local_file.FILEPATH)
    with open(local_file.FILEPATH, "rb") as f:
        original = f.read()
    decoded = base64.b64decode(encoded)
    assert decoded == original


def test_local_image_to_base64_roundtrip() -> None:
    encoded = local_image.image_to_base64(local_image.FILEPATH)
    decoded = base64.b64decode(encoded)
    assert len(decoded) > 0


@pytest.mark.asyncio
async def test_stream_function_call_args_write_file() -> None:
    result = await _invoke_tool(
        stream_function_call_args.write_file,
        {"filename": "test.txt", "content": "hello"},
    )
    assert result == "File test.txt written successfully"


@pytest.mark.asyncio
async def test_stream_function_call_args_create_config() -> None:
    result = await _invoke_tool(
        stream_function_call_args.create_config,
        {
            "project_name": "demo",
            "version": "1.0.0",
            "dependencies": ["fastapi", "uvicorn"],
        },
    )
    assert result == "Config for demo v1.0.0 created"


@pytest.mark.asyncio
async def test_stream_items_how_many_jokes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stream_items.random, "randint", lambda _a, _b: 5)
    result = await _invoke_tool(stream_items.how_many_jokes, {})
    assert result == 5


def _make_guardrail_input(arguments: dict[str, Any]) -> ToolInputGuardrailData:
    agent = Agent(name="Guardrail", instructions="Testing")
    context = ToolContext(
        context=None,
        usage=Usage(),
        tool_name="send_email",
        tool_call_id="call_456",
        tool_arguments=json.dumps(arguments),
    )
    return ToolInputGuardrailData(context=context, agent=agent)


def _make_guardrail_output(arguments: dict[str, Any], output: Any) -> ToolOutputGuardrailData:
    agent = Agent(name="Guardrail", instructions="Testing")
    context = ToolContext(
        context=None,
        usage=Usage(),
        tool_name="get_user_data",
        tool_call_id="call_789",
        tool_arguments=json.dumps(arguments),
    )
    return ToolOutputGuardrailData(context=context, agent=agent, output=output)


def test_tool_guardrails_reject_sensitive_words() -> None:
    data = _make_guardrail_input({"subject": "Attempting to hack the system"})
    result = tool_guardrails.reject_sensitive_words.guardrail_function(data)
    assert result.behavior["type"] == "reject_content"
    assert "blocked_word" in result.output_info


def test_tool_guardrails_allow_non_sensitive_input() -> None:
    data = _make_guardrail_input({"subject": "Hello world"})
    result = tool_guardrails.reject_sensitive_words.guardrail_function(data)
    assert result.behavior["type"] == "allow"


def test_tool_guardrails_block_sensitive_output() -> None:
    data = _make_guardrail_output({}, {"ssn": "123-45-6789"})
    result = tool_guardrails.block_sensitive_output.guardrail_function(data)
    assert result.behavior["type"] == "raise_exception"
    assert result.output_info["blocked_pattern"] == "SSN"


def test_tool_guardrails_reject_phone_numbers() -> None:
    data = _make_guardrail_output({}, {"phone": "555-1234"})
    result = tool_guardrails.reject_phone_numbers.guardrail_function(data)
    assert result.behavior["type"] == "reject_content"

    data = _make_guardrail_output({}, {"phone": "555-9999"})
    result = tool_guardrails.reject_phone_numbers.guardrail_function(data)
    assert result.behavior["type"] == "allow"


@pytest.mark.asyncio
async def test_usage_tracking_get_weather_tool() -> None:
    result = await _invoke_tool(usage_tracking.get_weather, {"city": "Berlin"})
    assert result.city == "Berlin"


def test_usage_tracking_print_usage(capsys: pytest.CaptureFixture[str]) -> None:
    usage = Usage(requests=2, input_tokens=10, output_tokens=5, total_tokens=15)
    usage_tracking.print_usage(usage)
    captured = capsys.readouterr().out
    assert "=== Usage ===" in captured
    assert "Requests: 2" in captured
    assert "Input tokens: 10" in captured
    assert "Output tokens: 5" in captured
    assert "Total tokens: 15" in captured
