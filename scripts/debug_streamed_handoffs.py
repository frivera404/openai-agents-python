import asyncio
import json

from agents import Agent
from agents.run import Runner
from tests.fake_model import FakeModel
from tests.test_responses import get_function_tool_call, get_text_message


async def main():
    model = FakeModel()
    agent_1 = Agent(name="test", model=model)
    agent_2 = Agent(name="test", model=model)
    agent_3 = Agent(name="test", model=model, handoffs=[agent_1, agent_2])

    model.add_multiple_turn_outputs(
        [
            [get_function_tool_call("some_function", json.dumps({"a": "b"}))],
            [get_text_message("a_message"), get_function_tool_call("transfer_to_test", "")],
            [get_text_message("done")],
        ]
    )

    result = Runner.run_streamed(agent_3, input="user_message")
    async for _ in result.stream_events():
        pass

    print("final_output=", result.final_output)
    print("raw_responses_count=", len(result.raw_responses))
    print("new_items_count=", len(result.new_items))
    print("to_input_list_count=", len(result.to_input_list()))
    for i, it in enumerate(result.new_items):
        print(i, type(it), getattr(it, "type", None), getattr(it, "raw_item", None))


asyncio.run(main())
