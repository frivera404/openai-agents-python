from agents.extensions.models.litellm_model import InternalChatCompletionMessage
from agents.models.chatcmpl_converter import Converter
from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function

message = InternalChatCompletionMessage(
    role="assistant",
    content="I'll check the weather for you.",
    reasoning_content="The user wants weather information, I need to call the weather function",
    thinking_blocks=[
        {
            "type": "thinking",
            "thinking": (
                "The user is asking about weather. "
                "Let me use the weather tool to get this information."
            ),
            "signature": "TestSignature123",
        },
        {
            "type": "thinking",
            "thinking": ("We should use the city Tokyo as the city."),
            "signature": "TestSignature456",
        },
    ],
    tool_calls=[
        ChatCompletionMessageToolCall(
            id="call_123",
            type="function",
            function=Function(name="get_weather", arguments='{"city": "Tokyo"}'),
        )
    ],
)

output_items = Converter.message_to_output_items(message)
print("OUTPUT ITEMS:")
for i, it in enumerate(output_items):
    print(i, type(it), getattr(it, "type", None))
    if hasattr(it, "model_dump"):
        d = it.model_dump()
    else:
        d = dict(it)
    print("  DUMP:", d)

items_as_dicts = []
for item in output_items:
    if hasattr(item, "model_dump"):
        items_as_dicts.append(item.model_dump())
    else:
        items_as_dicts.append(dict(item))

print("\nITEMS AS DICTS:")
for i, d in enumerate(items_as_dicts):
    print(i, d)

messages = Converter.items_to_messages(items_as_dicts, preserve_thinking_blocks=True)
print("\nMESSAGES:")
for m in messages:
    print(m)
