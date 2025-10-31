"""FastAPI wrapper around the main agent controller."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from jsonschema import Draft7Validator, validate as js_validate
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv(dotenv_path=os.getenv("DOTENV_FILE", ".env"))

app = FastAPI(
    title="Main Agent API",
    version=os.getenv("APP_VERSION", "1.0.0"),
    description=(
        "HTTP wrapper for the Main Orchestrator Agent.\n\n"
        "Endpoints: /healthz, /chat (sync), /chat/stream (SSE), /chat/json (server-side JSON schema).\n\n"
        "Auth: set APP_API_KEY and pass X-API-Key header."
    ),
    contact={"name": "R-Unlimited LLC / R-U Creative"},
    license_info={"name": "Apache-2.0"},
    servers=[{"url": os.getenv("PUBLIC_BASE_URL", "")}] if os.getenv("PUBLIC_BASE_URL") else None,
)

APP_API_KEY = os.getenv("APP_API_KEY")


def require_api_key(x_api_key: Optional[str] = Header(None, description="Project API key")):
    if APP_API_KEY and x_api_key != APP_API_KEY:
        raise HTTPException(401, "Invalid or missing API key")


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY not set")
    base_url = os.getenv("OPENAI_BASE_URL")
    return OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)


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


JSON_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "basic_message": {
        "type": "object",
        "properties": {"msg": {"type": "string"}},
        "required": ["msg"],
        "additionalProperties": False,
    },
    "ideas_list": {
        "type": "object",
        "properties": {
            "ideas": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["ideas"],
        "additionalProperties": False,
    },
}


class ChatReq(BaseModel):
    prompt: str = Field(..., description="User prompt")
    system: str | None = Field(None, description="System instructions")
    model: str = Field(default=os.getenv("GPT_CLI_MODEL", "gpt-4o"), description="OpenAI model")
    temperature: float = Field(default=0.2, ge=0, le=2, description="Sampling temperature")
    json_only: bool = Field(default=False, description="Ask model to return minified JSON only")
    json_schema: dict | None = Field(None, description="Inline JSON Schema to validate response")


class ChatResp(BaseModel):
    ok: bool
    content: str | None = None


class JsonChatReq(BaseModel):
    prompt: str = Field(..., description="User prompt")
    system: str | None = None
    model: str = Field(default=os.getenv("GPT_CLI_MODEL", "gpt-4o"))
    temperature: float = Field(default=0.2, ge=0, le=2)
    schema_name: str = Field(..., description=f"One of: {', '.join(JSON_SCHEMAS.keys())}")


class JsonChatResp(BaseModel):
    ok: bool
    content: dict | None = None
    schema_name: str


@app.get("/healthz", tags=["meta"])
async def healthz():
    return {"ok": True, "env": os.getenv("APP_ENV", "dev")}


@app.post("/chat", response_model=ChatResp, tags=["chat"])
async def chat(r: ChatReq, _=Depends(require_api_key)):
    messages: List[Dict[str, Any]] = []
    if r.system:
        messages.append({"role": "system", "content": r.system})
    if r.json_only:
        messages.append({"role": "system", "content": "Return ONLY valid minified JSON. No prose."})
    messages.append({"role": "user", "content": r.prompt})
    try:
        resp = _client().chat.completions.create(
            model=r.model, messages=messages, temperature=r.temperature, tools=tool_schemas
        )
        msg = resp.choices[0].message
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                tool_result = run_tool_call(tc.function.name, tc.function.arguments)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": tool_result})
            resp = _client().chat.completions.create(
                model=r.model, messages=messages, temperature=r.temperature
            )
        content = resp.choices[0].message.content or ""
        if r.json_only and r.json_schema:
            Draft7Validator.check_schema(r.json_schema)
            js_validate(instance=json.loads(content), schema=r.json_schema)
        return {"ok": True, "content": content}
    except Exception as e:
        raise HTTPException(500, f"API error: {e}")


@app.post("/chat/stream", tags=["chat"])
async def chat_stream(r: ChatReq, _=Depends(require_api_key)):
    messages: List[Dict[str, Any]] = []
    if r.system:
        messages.append({"role": "system", "content": r.system})
    if r.json_only:
        messages.append({"role": "system", "content": "Return ONLY valid minified JSON. No prose."})
    messages.append({"role": "user", "content": r.prompt})
    try:
        stream = _client().chat.completions.create(
            model=r.model, messages=messages, temperature=r.temperature, stream=True
        )
    except Exception as e:
        raise HTTPException(500, f"API error: {e}")

    async def event_gen():
        try:
            for chunk in stream:  # type: ignore[assignment]
                data = getattr(chunk.choices[0].delta, "content", None)
                if data:
                    yield f"data: {json.dumps({'chunk': data})}\n\n"
            yield "event: done\ndata: {}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.post(
    "/chat/json",
    response_model=JsonChatResp,
    tags=["chat"],
    summary="Strict JSON by named schema",
    description="Model is instructed to return minified JSON. Server validates against the named schema and returns a parsed object.",
)
async def chat_json(r: JsonChatReq, _=Depends(require_api_key)):
    schema = JSON_SCHEMAS.get(r.schema_name)
    if not schema:
        raise HTTPException(400, f"Unknown schema_name: {r.schema_name}")

    messages: List[Dict[str, Any]] = []
    sys_hint = (
        "Return ONLY valid minified JSON that conforms to the provided JSON Schema. No code fences, no prose."
    )
    if r.system:
        messages.append({"role": "system", "content": r.system})
    messages.append({"role": "system", "content": sys_hint})
    messages.append({"role": "system", "content": f"JSON Schema: {json.dumps(schema, separators=(',', ':'))}"})
    messages.append({"role": "user", "content": r.prompt})

    try:
        resp = _client().chat.completions.create(
            model=r.model, messages=messages, temperature=r.temperature
        )
        raw = resp.choices[0].message.content or "{}"
        obj = json.loads(raw)
        Draft7Validator.check_schema(schema)
        js_validate(instance=obj, schema=schema)
        return {"ok": True, "content": obj, "schema_name": r.schema_name}
    except Exception as e:
        raise HTTPException(500, f"API error or JSON validation failed: {e}")


async def _ensure_event_loop() -> None:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


asyncio.run(_ensure_event_loop())
