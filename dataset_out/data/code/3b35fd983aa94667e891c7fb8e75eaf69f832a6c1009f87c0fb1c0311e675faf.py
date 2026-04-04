import asyncio

from agents import Agent, Usage
from agents._run_impl import RunHooks, RunImpl
from agents.items import ModelResponse
from agents.run import RunConfig
from agents.run_context import RunContextWrapper
from agents.tool import function_tool
from openai.types.responses import (
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputText,
)


async def main():
    agent = Agent(name="test", tools=[function_tool(lambda: "123", name_override="test")])
    response = ModelResponse(
        output=[
            ResponseOutputMessage(
                id="1",
                type="message",
                role="assistant",
                content=[
                    ResponseOutputText(text="hello_world", type="output_text", annotations=[])
                ],
                status="completed",
            ),
            ResponseFunctionToolCall(
                id="1", call_id="2", type="function_call", name="test", arguments=""
            ),
        ],
        usage=Usage(),
        response_id=None,
    )

    processed_response = RunImpl.process_model_response(
        agent=agent,
        all_tools=await agent.get_all_tools(RunContextWrapper(None)),
        response=response,
        output_schema=None,
        handoffs=[],
    )

    result = await RunImpl.execute_tools_and_side_effects(
        agent=agent,
        original_input="hello",
        new_response=response,
        pre_step_items=[],
        processed_response=processed_response,
        output_schema=None,
        hooks=RunHooks(),
        context_wrapper=RunContextWrapper(None),
        run_config=RunConfig(),
    )

    print("generated_items count=", len(result.generated_items))
    for i, it in enumerate(result.generated_items):
        print(i, type(it), getattr(it, "type", None), getattr(it, "raw_item", None))


asyncio.run(main())
