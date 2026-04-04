from agents.models.chatcmpl_converter import Converter
from tests.test_anthropic_thinking_blocks import create_mock_anthropic_response_with_thinking

m = create_mock_anthropic_response_with_thinking()
outs = Converter.message_to_output_items(m)
print("output_items types:")
for o in outs:
    print(type(o), getattr(o, "type", None))

items_as_dicts = [o.model_dump() if hasattr(o, "model_dump") else o for o in outs]
print("\nitems_as_dicts:")
for d in items_as_dicts:
    print(d.get("type"), "content=", d.get("content"))
print("\nfull items_as_dicts:")
for d in items_as_dicts:
    print(d)
