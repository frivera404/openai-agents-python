"""
Agent Autonomy Fine-tuning Helper

Generates a JSONL dataset for instruction/fine-tuning that teaches agents
how and when to call their tools. It can discover `FunctionTool` instances
exported by modules you point it at and synthesize prompt/completion pairs
showing the tool call pattern.

Usage examples:

# Discover tools from modules and write dataset
# Example:
#   python scripts/agent_autonomy_finetune.py \
#       --modules agents.workers.research_bot \
#       --output data/autonomy_train.jsonl

# Generate dataset and attempt an OpenAI fine-tune (requires OPENAI_API_KEY)
# Example:
#   python scripts/agent_autonomy_finetune.py \
#       --modules agents.workers.research_bot \
#       --output data/autonomy_train.jsonl \
#       --fine-tune --openai-model "gpt-4o-mini"

Notes:
- This script generates synthetic examples. For production-quality tuning,
  provide curated human-written examples in `--examples-dir` (JSONL of prompt/completion pairs).
- The OpenAI fine-tune path is optional and best-effort; it requires the `openai` package
  and an API key in `OPENAI_API_KEY`.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
from collections.abc import Iterable
from dataclasses import is_dataclass
from typing import Any


def discover_function_tools(module_names: Iterable[str]) -> list[tuple[str, Any]]:
    """Import modules and return a list of (qualname, FunctionTool instance).

    We look for dataclass instances of the type `FunctionTool` defined in
    `agents.tool`. This is a best-effort discovery; you can also pass
    explicit tool modules that export configured FunctionTool objects.
    """
    tools = []
    for mod_name in module_names:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"Warning: failed to import {mod_name}: {e}")
            continue

        for name, val in vars(mod).items():
            # Best-effort: dataclass instances with `name` and `params_json_schema`
            if is_dataclass(val):
                # Likely a class, skip
                continue
            try:
                type(val)
                qual = f"{mod_name}.{name}"
                # Heuristic: has fields used by FunctionTool
                if (
                    hasattr(val, "name")
                    and hasattr(val, "params_json_schema")
                    and hasattr(val, "description")
                ):
                    tools.append((qual, val))
            except Exception:
                continue

    return tools


def synthesize_examples_for_tool(tool: Any, n: int = 5) -> list[dict[str, str]]:
    """Produce synthetic prompt/completion pairs for a single tool.

    The `prompt` is an instruction describing a user intent where calling
    the tool is appropriate. The `completion` shows an assistant function
    call encoded as a JSON string followed by a short text response.
    """
    out = []
    name = getattr(tool, "name", "tool")
    desc = getattr(tool, "description", "")
    schema = getattr(tool, "params_json_schema", {})

    # A few templated user intents. In practice you should supply real examples.
    templates = [
        f"Use the `{name}` tool to perform its task: {desc}",
        f"I need the result of calling {name} with appropriate args.",
        f"When should we call the {name} tool? Call it when the user asks for {desc}.",
    ]

    for i in range(n):
        prompt = (
            templates[i % len(templates)] + "\nAvailable tools:\n" + f"- {name}: {desc}\nAssistant:"
        )

        # Build a small example arguments object by filling schema's properties with placeholders
        args = {}
        props = schema.get("properties", {}) if isinstance(schema, dict) else {}
        for k in list(props)[:3]:
            args[k] = f"<{k}>"


        # Completion: mimic a model function call representation followed by final textual reply
        completion = (
            json.dumps({"type": "function_call", "name": name, "arguments": args})
            + "\n"
            + json.dumps({"type": "tool_response", "result": "<tool output here>"})
            + "\nAssistant: Here is the result from the tool."
        )

        out.append({"prompt": prompt, "completion": completion})

    return out


def load_examples_dir(path: str) -> list[dict[str, str]]:
    """Load user-provided JSONL examples from a directory or single file."""
    examples = []
    if os.path.isdir(path):
        for fn in sorted(os.listdir(path)):
            if not fn.lower().endswith(".jsonl"):
                continue
            with open(os.path.join(path, fn), encoding="utf-8") as f:
                for line in f:
                    examples.append(json.loads(line))
    elif os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                examples.append(json.loads(line))
    return examples


def write_jsonl(items: Iterable[dict[str, str]], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path}")


def maybe_run_openai_finetune(file_path: str, model: str) -> None:
    """Best-effort attempt to create a fine-tune job using `openai` package.

    This requires `openai` to be installed and `OPENAI_API_KEY` set in env.
    If either is missing, we print instructions for the user instead.
    """
    try:
        import openai
    except Exception:
        print(
            "openai package not available — skipping automatic fine-tune."
        )
        print("Install via: pip install openai")
        return

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set — cannot call OpenAI fine-tune API.")
        return

    print("Attempting to upload dataset and create fine-tune job (best-effort).")

    # Support both OpenAI Python pre-1.0 and 1.x+ client styles.
    # Preferred (1.x+): from openai import OpenAI; client = OpenAI(); client.files.create(...)
    try:
        # Try modern client first
        OpenAI = getattr(openai, "OpenAI", None)
        if OpenAI:
            client = OpenAI()
            with open(file_path, "rb") as f:
                resp = client.files.create(file=f, purpose="fine-tune")
            print("Uploaded file:", resp)
            # resp may expose `id` attribute or be a mapping
            resp_id = getattr(resp, "id", None) or (
                resp.get("id") if isinstance(resp, dict) else None
            )
            # Some OpenAI client builds may not expose a fine_tunes helper;
            # fall back to REST if needed.
            try:
                if hasattr(client, "fine_tunes"):
                    ft = client.fine_tunes.create(training_file=resp_id, model=model)
                    print("Created fine-tune job:", ft)
                    return
                else:
                    raise AttributeError("client has no fine_tunes attribute")
            except Exception as e_create:
                # REST fallback
                try:
                    import requests

                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    payload = {"training_file": resp_id, "model": model}
                    r = requests.post(
                        "https://api.openai.com/v1/fine_tunes", headers=headers, json=payload
                    )
                    print("Created fine-tune job via REST:", r.status_code, r.text)
                    return
                except Exception as e_rest:
                    print("Failed to create fine-tune job via client and REST:", e_create, e_rest)
    except Exception as e_modern:
        print("Modern OpenAI client flow failed, falling back to legacy API:", e_modern)

    # Fallback to legacy (pre-1.0) API surface
    try:
        openai.api_key = api_key
        with open(file_path, "rb") as f:
            # legacy SDK used openai.File.create
            resp = openai.File.create(file=f, purpose="fine-tune")
        print("Uploaded file:", resp)
        # legacy response indexed by id
        resp_id = resp.get("id") if isinstance(resp, dict) else getattr(resp, "id", None)
        ft = openai.FineTune.create(training_file=resp_id, model=model)
        print("Created fine-tune job:", ft)
    except Exception as e_legacy:
        print("Failed to create fine-tune job:", e_legacy)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--modules", nargs="*", help="Modules to scan for FunctionTool instances", default=[]
    )
    p.add_argument(
        "--output", help="Output JSONL training file", default="data/autonomy_train.jsonl"
    )
    p.add_argument(
        "--examples-dir",
        help="Directory or file of existing JSONL examples to include",
        default=None,
    )
    p.add_argument("--examples-per-tool", type=int, default=5)
    p.add_argument(
        "--fine-tune",
        action="store_true",
        help="Attempt to call OpenAI fine-tune API with generated file",
    )
    p.add_argument(
        "--openai-model", default="gpt-4.1", help="Model to use for fine-tune (if supported)"
    )
    args = p.parse_args(argv)

    all_examples: list[dict[str, str]] = []

    if args.examples_dir:
        ext = load_examples_dir(args.examples_dir)
        all_examples.extend(ext)

    if args.modules:
        tools = discover_function_tools(args.modules)
        if not tools:
            print("No FunctionTool instances discovered in modules.")
        for qual, tool in tools:
            print(f"Generating examples for {qual} ({tool.name})")
            ex = synthesize_examples_for_tool(tool, n=args.examples_per_tool)
            all_examples.extend(ex)

    if not all_examples:
        print("No examples produced — write manual examples or provide --modules / --examples-dir.")
        return

    write_jsonl(all_examples, args.output)

    if args.fine_tune:
        maybe_run_openai_finetune(args.output, args.openai_model)


if __name__ == "__main__":
    main()
