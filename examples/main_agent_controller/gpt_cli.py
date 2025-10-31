#!/usr/bin/env python3
"""Command line controller for running the main orchestrator agent."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import sys
import time
from typing import Any, Dict, List

from jsonschema import Draft7Validator, validate as jsonschema_validate
from openai import OpenAI

DEF_MODEL = os.getenv("GPT_CLI_MODEL", "gpt-4o")
HIST_PATH = pathlib.Path(os.getenv("GPT_CLI_HISTORY", "~/.gpt_cli/history.json")).expanduser()
HIST_PATH.parent.mkdir(parents=True, exist_ok=True)


# --------- storage ---------

def _read_json(path: pathlib.Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _write_json(path: pathlib.Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2))


def load_history(session: str) -> List[Dict[str, Any]]:
    return _read_json(HIST_PATH).get(session, [])


def save_history(session: str, messages: List[Dict[str, Any]]) -> None:
    data = _read_json(HIST_PATH)
    data[session] = messages
    _write_json(HIST_PATH, data)


# --------- helpers ---------

def attach_files(files: List[str]) -> List[Dict[str, Any]]:
    parts = []
    for f in files or []:
        p = pathlib.Path(f)
        if not p.exists():
            continue
        try:
            text = p.read_text(errors="ignore")
            parts.append(
                f"\n--- file:{p.name} ---\n{text}\n"
            )
        except Exception:
            parts.append(
                f"\n--- file:{p.name} (binary/unreadable) ---\n"
            )
    return ([{"role": "user", "content": "".join(parts)}] if parts else [])


# --------- tools (schema + simple example) ---------

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "ping",
            "description": "Return a short pong with optional message.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": [],
            },
        },
    }
]


def run_tool_call(name: str, arguments_json: str) -> str:
    try:
        args = json.loads(arguments_json or "{}")
    except Exception:
        args = {}
    if name == "ping":
        return json.dumps({"pong": True, "echo": args.get("message", "")})
    return json.dumps({"error": f"unknown tool {name}"})


# --------- core call ---------

def call_openai(
    messages: List[Dict[str, Any]],
    *,
    model: str,
    stream: bool,
    retries: int = 3,
    temp: float = 0.2,
    use_tools: bool = True,
):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    backoff = 1.0
    for attempt in range(retries):
        try:
            kwargs = dict(model=model, messages=messages, temperature=temp)
            if use_tools:
                kwargs["tools"] = tool_schemas
            if stream:
                return client.chat.completions.create(stream=True, **kwargs)
            return client.chat.completions.create(**kwargs)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(backoff)
            backoff = min(backoff * 2, 8)
    raise RuntimeError("Failed to call OpenAI after retries")


# --------- CLI ---------

def main() -> None:
    ap = argparse.ArgumentParser(
        prog="gpt",
        description="GPT-4o CLI with sessions, streaming, JSON schema, tools.",
    )
    ap.add_argument("prompt", nargs="*", help="Prompt text (omit to read from STDIN)")
    ap.add_argument("--session", default="default", help="Session name (for history)")
    ap.add_argument("-m", "--model", default=DEF_MODEL, help=f"Model (default {DEF_MODEL})")
    ap.add_argument("-s", "--system", default=None, help="System instructions for this run")
    ap.add_argument("--reset", action="store_true", help="Reset session history before run")
    ap.add_argument("--files", nargs="*", default=[], help="Inline small text files as context")
    ap.add_argument("--stream", action="store_true", help="Stream tokens to stdout")
    ap.add_argument("--json-only", action="store_true", help="Return ONLY JSON and validate")
    ap.add_argument("--json-schema", default=None, help="Path to a JSON Schema file for validation")
    ap.add_argument("--no-save", action="store_true", help="Do not persist history")
    ap.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature")
    ap.add_argument("--retries", type=int, default=3, help="Retry count for API errors")
    ap.add_argument("--no-tools", action="store_true", help="Disable tool calling")
    args = ap.parse_args()

    user_text = " ".join(args.prompt).strip() or sys.stdin.read().strip()
    if not user_text:
        print("ERROR: No prompt provided.", file=sys.stderr)
        sys.exit(2)

    messages = [] if args.reset else load_history(args.session)
    if args.system:
        messages = [m for m in messages if m.get("role") != "system"]
        messages.insert(0, {"role": "system", "content": args.system})

    if args.json_only:
        messages.insert(0, {"role": "system", "content": "Return ONLY valid minified JSON. No prose."})

    messages.extend(attach_files(args.files))
    messages.append({"role": "user", "content": user_text})

    def tool_loop_once(resp_obj):
        msg = resp_obj.choices[0].message
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                tool_name = tc.function.name
                tool_args = tc.function.arguments
                tool_result = run_tool_call(tool_name, tool_args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_result})
            return call_openai(
                messages,
                model=args.model,
                stream=False,
                retries=args.retries,
                temp=args.temperature,
                use_tools=(not args.no_tools),
            )
        return resp_obj

    try:
        if args.stream:
            res = call_openai(
                messages,
                model=args.model,
                stream=True,
                retries=args.retries,
                temp=args.temperature,
                use_tools=(not args.no_tools),
            )
            out_buf = []
            for chunk in res:  # type: ignore[union-attr]
                delta = getattr(chunk.choices[0].delta, "content", None)
                if delta:
                    sys.stdout.write(delta)
                    sys.stdout.flush()
                    out_buf.append(delta)
            print()
            content = "".join(out_buf)
        else:
            res = call_openai(
                messages,
                model=args.model,
                stream=False,
                retries=args.retries,
                temp=args.temperature,
                use_tools=(not args.no_tools),
            )
            res = tool_loop_once(res)
            content = res.choices[0].message.content or ""
            print(content)
    except Exception as e:
        print(f"API ERROR: {e}", file=sys.stderr)
        sys.exit(3)

    if args.json_only and args.json_schema:
        try:
            schema = json.loads(pathlib.Path(args.json_schema).read_text())
            Draft7Validator.check_schema(schema)
            jsonschema_validate(json.loads(content), schema)
        except Exception as e:
            print(f"\nERROR: JSON Schema validation failed: {e}", file=sys.stderr)
            sys.exit(4)

    if not args.no_save:
        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "system", "content": f"[meta] run at {datetime.datetime.utcnow().isoformat()}Z"})
        save_history(args.session, messages)


if __name__ == "__main__":
    main()
