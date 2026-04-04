"""
Generate demo autonomy dataset using local `FunctionTool` constructors.
This script does not attempt to discover real module-level FunctionTool
instances; instead it demonstrates dataset generation by creating a couple
of illustrative `FunctionTool` objects and synthesizing examples.
"""

from __future__ import annotations

import json
import os

from agents.tool import FunctionTool

OUT = "data/autonomy_demo.jsonl"

TOOLS = [
    FunctionTool(
        name="get_weather",
        description="Fetch current weather for a city",
        params_json_schema={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
        on_invoke_tool=lambda ctx, args: None,
    ),
    FunctionTool(
        name="search_web",
        description="Search the web for query and return top results",
        params_json_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["query"],
        },
        on_invoke_tool=lambda ctx, args: None,
    ),
]

examples = []
for tool in TOOLS:
    name = tool.name
    desc = tool.description
    schema = tool.params_json_schema
    # produce 3 examples each
    for _i in range(3):
        prompt = f"User asks for {desc}. Available tool: {name}"
        props = schema.get("properties", {})
        args = {k: f"<{k}>" for k in list(props)[:2]}
        completion = json.dumps({"type": "function_call", "name": name, "arguments": args})
        examples.append({"prompt": prompt, "completion": completion})

os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")
print(f"Wrote demo dataset to {OUT}")
