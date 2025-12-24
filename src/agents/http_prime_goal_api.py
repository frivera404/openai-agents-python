import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl, BaseModel

from openai_assistant_agent import AgentConfigurator, OpenAIAssistantAgent

from .supervisor import SupervisorOrchestrator
from .ctdatenight_agents import (
    make_shopkeeper_agent,
    make_supervisor_agent,
    make_retention_agent,
    make_info_agent,
)

app = FastAPI(title="Agent Private I - Prime Goal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"ok": True}


class PrimeGoalStatus(BaseModel):
    prime_goal_active: bool
    supervisor_agents_configured: int
    total_supervisor_agents: int
    system_optimizations_active: bool
    configuration_integrity: bool


class ActionResult(BaseModel):
    success: bool
    detail: str
    status: Optional[PrimeGoalStatus] = None


class SupervisorAgent(BaseModel):
    id: str
    name: str
    role: str
    optimization_level: str


class SystemSettings(BaseModel):
    global_optimizations: Dict[str, Any]
    mcp_integration: Dict[str, Any]


class CommandRequest(BaseModel):
    supervisor_id: str
    command: str


class CommandResponse(BaseModel):
    supervisor_id: str
    supervisor_name: str
    content: str
    created_at: str


class ToolDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    usage: Optional[str] = None


class AgentQueryRequest(BaseModel):
    """Request body for running a natural language query through the agent."""

    query: str
    thread_id: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Structured response from the OpenAI Assistant agent."""

    query: str
    response: str
    thread_id: Optional[str] = None
    timestamp: float


class FilesystemPathRequest(BaseModel):
    """Request body for filesystem MCP calls."""

    path: str


class FilesystemOpRequest(BaseModel):
    """Request body for combined filesystem operation endpoint."""

    op: str
    path: str

    # Only used when op == "search"
    query: Optional[str] = None
    max_results: Optional[int] = 20


class FilesystemSearchRequest(BaseModel):
    """Request body for filesystem search via MCP."""

    path: str
    query: str
    max_results: int = 20


class SupervisorPlan(BaseModel):
    selected_sub_agent_id: str
    selected_sub_agent_name: str
    selected_sub_agent_role: str
    selected_sub_agent_description: str


class SupervisorQueryResponse(BaseModel):
    """Response for a supervised query.

    Includes the supervisor's plan (which sub-agent was selected) and the
    underlying agent's result.
    """

    plan: SupervisorPlan
    result: AgentQueryResponse


agent = OpenAIAssistantAgent()
configurator = AgentConfigurator()

# Instantiate specialized CTDateNight agents and register them with the supervisor
shopkeeper_agent = make_shopkeeper_agent()
retention_agent = make_retention_agent()
info_agent = make_info_agent()
supervisor_agent = make_supervisor_agent()

sub_agent_instances = {
    "shopkeeper": shopkeeper_agent,
    "retention": retention_agent,
    "info": info_agent,
    "supervisor": supervisor_agent,
}

supervisor_orchestrator = SupervisorOrchestrator(agent, sub_agent_instances=sub_agent_instances)


_mcp_initialized: bool = False
_mcp_init_lock = asyncio.Lock()


async def _ensure_mcp_initialized() -> None:
    """Lazily initialize MCP servers once.

    This keeps startup fast and allows using MCP tools (like web search)
    even when OpenAI model access is unavailable.
    """

    global _mcp_initialized
    if _mcp_initialized:
        return

    async with _mcp_init_lock:
        if _mcp_initialized:
            return

        await agent.initialize_mcp_servers()
        _mcp_initialized = True


_agent_initialized: bool = False
_agent_init_lock = asyncio.Lock()


# --- Automation storage + scheduler ---

_AUTOMATION_STORE_PATH = Path(__file__).resolve().parents[2] / "automation_store.json"

_automation_lock = asyncio.Lock()
_automation_loaded = False

_webhooks: Dict[str, Dict[str, Any]] = {}
_schedules: Dict[str, Dict[str, Any]] = {}

_scheduler_task: Optional[asyncio.Task[None]] = None
_scheduler_wakeup = asyncio.Event()


_WIN_DRIVE_RE = re.compile(r"^([A-Za-z]):\\(.*)$")


def _map_path_for_docker_filesystem(path: str) -> str:
    r"""Map Windows/local paths to container-visible paths.

    - Repo root is mounted at /workspace
    - C:\Users\frive is mounted at /host/C/Users/frive
    """

    p = (path or "").strip()
    if not p:
        return p

    # Map absolute Windows paths like C:\Users\frive\... -> /host/C/Users/frive/...
    m = _WIN_DRIVE_RE.match(p)
    if m:
        drive = m.group(1).upper()
        rest = m.group(2).replace("\\", "/")
        return f"/host/{drive}/{rest}"

    # Map local repo-root paths -> /workspace/...
    try:
        repo_root = Path(__file__).resolve().parents[2]
        candidate = Path(p)
        if candidate.is_absolute() and str(candidate).lower().startswith(str(repo_root).lower()):
            rel = candidate.relative_to(repo_root).as_posix()
            return f"/workspace/{rel}" if rel else "/workspace"
    except Exception:
        pass

    return p


def _load_automation_store_sync() -> Dict[str, Any]:
    if not _AUTOMATION_STORE_PATH.exists():
        return {"webhooks": {}, "schedules": {}}

    with _AUTOMATION_STORE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {"webhooks": {}, "schedules": {}}

    webhooks = data.get("webhooks", {})
    schedules = data.get("schedules", {})
    return {
        "webhooks": webhooks if isinstance(webhooks, dict) else {},
        "schedules": schedules if isinstance(schedules, dict) else {},
    }


def _save_automation_store_sync(data: Dict[str, Any]) -> None:
    tmp = _AUTOMATION_STORE_PATH.with_suffix(".json.tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    tmp.replace(_AUTOMATION_STORE_PATH)


async def _ensure_automation_loaded() -> None:
    global _automation_loaded, _webhooks, _schedules
    if _automation_loaded:
        return

    async with _automation_lock:
        if _automation_loaded:
            return

        data = await asyncio.to_thread(_load_automation_store_sync)
        _webhooks = data.get("webhooks", {})
        _schedules = data.get("schedules", {})
        _automation_loaded = True


async def _save_automation_store() -> None:
    await _ensure_automation_loaded()
    async with _automation_lock:
        snapshot = {
            "webhooks": dict(_webhooks),
            "schedules": dict(_schedules),
            "updated_at": datetime.now().isoformat(),
        }
    await asyncio.to_thread(_save_automation_store_sync, snapshot)


def _jsonable(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    if hasattr(obj, "model_dump"):
        try:
            return _jsonable(obj.model_dump())
        except Exception:
            return str(obj)
    if hasattr(obj, "dict"):
        try:
            return _jsonable(obj.dict())
        except Exception:
            return str(obj)
    return str(obj)


async def _call_first_available_mcp_tool(
    tool_names: List[str], arguments: Dict[str, Any]
) -> Dict[str, Any]:
    await _ensure_mcp_initialized()

    if not agent.mcp_servers:
        raise HTTPException(
            status_code=503,
            detail="No MCP servers are connected; enable/configure an MCP web-search server.",
        )

    last_error: Optional[str] = None
    for server in agent.mcp_servers:
        try:
            tools = await server.list_tools()
            available = {getattr(t, "name", str(t)) for t in tools}
            for name in tool_names:
                if name in available:
                    result = await server.call_tool(name, arguments)
                    return {
                        "server": getattr(server, "name", "unknown"),
                        "tool": name,
                        "result": _jsonable(result),
                    }
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            continue

    raise HTTPException(
        status_code=404,
        detail=(
            f"None of the tools {tool_names} were found on connected MCP servers."
            + (f" Last error: {last_error}" if last_error else "")
        ),
    )


async def _dispatch_to_webhook(webhook: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    url = webhook.get("url")
    if not url:
        return {"ok": False, "error": "Missing webhook url"}

    headers: Dict[str, str] = {}
    if webhook.get("secret"):
        headers["X-Webhook-Secret"] = str(webhook["secret"])

    timeout = httpx.Timeout(15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(str(url), json=payload, headers=headers)

    return {"ok": resp.is_success, "status_code": resp.status_code, "text": resp.text[:2000]}


async def _run_schedule(schedule_id: str) -> None:
    await _ensure_automation_loaded()

    async with _automation_lock:
        schedule = dict(_schedules.get(schedule_id, {}))

    if not schedule or not schedule.get("enabled", True):
        return

    kind = schedule.get("kind", "agent_query")
    query = schedule.get("query", "")
    webhook_ids = schedule.get("webhook_ids") or []

    started_at = time.time()
    ok = True
    error: Optional[str] = None
    result_payload: Dict[str, Any] = {
        "schedule_id": schedule_id,
        "kind": kind,
        "query": query,
        "started_at": started_at,
    }

    try:
        if kind == "web_search":
            search = await _call_first_available_mcp_tool(
                ["tavily_search", "web_search"],
                {"query": query},
            )
            result_payload["search"] = search
        else:
            await _ensure_agent_initialized()
            agent_result = await agent.run_query(query)
            if agent_result is None:
                raise RuntimeError("Agent failed to process query")
            result_payload["agent"] = agent_result

        deliveries: Dict[str, Any] = {}
        async with _automation_lock:
            targets = [
                (wid, _webhooks.get(wid))
                for wid in webhook_ids
                if isinstance(wid, str) and _webhooks.get(wid)
            ]

        for wid, wh in targets:
            if not wh or not wh.get("enabled", True):
                deliveries[wid] = {"ok": False, "error": "Webhook disabled or missing"}
                continue
            try:
                deliveries[wid] = await _dispatch_to_webhook(wh, result_payload)
            except Exception as e:
                deliveries[wid] = {"ok": False, "error": f"{type(e).__name__}: {e}"}

        result_payload["deliveries"] = deliveries

    except Exception as e:
        ok = False
        error = f"{type(e).__name__}: {e}"

    finished_at = time.time()
    async with _automation_lock:
        s = _schedules.get(schedule_id)
        if s is not None:
            s["last_run_at"] = finished_at
            s["last_run_ok"] = ok
            s["last_run_error"] = error
            s["last_duration_seconds"] = max(0.0, finished_at - started_at)

    await _save_automation_store()


async def _scheduler_loop() -> None:
    await _ensure_automation_loaded()

    while True:
        await _ensure_automation_loaded()

        async with _automation_lock:
            enabled = [
                (sid, s)
                for sid, s in _schedules.items()
                if s.get("enabled", True) and isinstance(s.get("next_run_at"), (int, float))
            ]

        if not enabled:
            _scheduler_wakeup.clear()
            await _scheduler_wakeup.wait()
            continue

        next_run_at = min(float(s.get("next_run_at")) for _, s in enabled)
        delay = max(0.0, next_run_at - time.time())

        _scheduler_wakeup.clear()
        try:
            await asyncio.wait_for(_scheduler_wakeup.wait(), timeout=delay)
            continue
        except asyncio.TimeoutError:
            pass

        due: List[str] = []
        now = time.time()
        async with _automation_lock:
            for sid, s in _schedules.items():
                if not s.get("enabled", True):
                    continue
                nr = s.get("next_run_at")
                if isinstance(nr, (int, float)) and float(nr) <= now:
                    due.append(sid)
                    interval = int(s.get("interval_seconds", 60))
                    s["next_run_at"] = now + max(1, interval)

        if due:
            await _save_automation_store()
            for sid in due:
                asyncio.create_task(_run_schedule(sid))


def _ensure_scheduler_started() -> None:
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(_scheduler_loop())


@app.on_event("startup")
async def _startup_automation() -> None:
    await _ensure_automation_loaded()
    _ensure_scheduler_started()


class WebhookCreateRequest(BaseModel):
    url: AnyHttpUrl
    secret: Optional[str] = None
    enabled: bool = True


class WebhookResponse(BaseModel):
    id: str
    url: AnyHttpUrl
    enabled: bool
    created_at: str


class ScheduleCreateRequest(BaseModel):
    kind: str = "agent_query"  # agent_query | web_search
    query: str
    interval_seconds: int = 300
    webhook_ids: List[str] = []
    enabled: bool = True


class ScheduleResponse(BaseModel):
    id: str
    kind: str
    query: str
    interval_seconds: int
    webhook_ids: List[str]
    enabled: bool
    next_run_at: float
    created_at: str
    last_run_at: Optional[float] = None
    last_run_ok: Optional[bool] = None
    last_run_error: Optional[str] = None


class AutomationRunRequest(BaseModel):
    kind: str = "agent_query"  # agent_query | web_search
    query: str
    webhook_ids: List[str] = []


async def _ensure_agent_initialized() -> None:
    """Lazily initialize MCP servers and create the agent once.

    This keeps startup fast but ensures the first real query has
    access to tools and a fully configured agent.
    """

    global _agent_initialized
    if _agent_initialized:
        return

    async with _agent_init_lock:
        if _agent_initialized:
            return

        # Ensure MCP servers are ready, then create the agent.
        await _ensure_mcp_initialized()
        created = agent.create_agent()
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create OpenAI assistant agent")

        _agent_initialized = True


@app.get("/agent/prime-goal/status", response_model=PrimeGoalStatus)
def get_prime_goal_status() -> PrimeGoalStatus:
    status: Dict[str, Any] = configurator.verify_prime_goal_status(agent)
    return PrimeGoalStatus(**status)


@app.post("/agent/prime-goal/apply", response_model=ActionResult)
def apply_prime_goal() -> ActionResult:
    success = agent.apply_prime_goal_configuration()
    status_dict: Dict[str, Any] = configurator.verify_prime_goal_status(agent)
    status = PrimeGoalStatus(**status_dict)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to apply Prime Goal configuration")
    return ActionResult(success=True, detail="Prime Goal configuration applied", status=status)


@app.post("/agent/prime-goal/reset", response_model=ActionResult)
def reset_prime_goal() -> ActionResult:
    success = agent.reset_to_prime_goal(confirm=True)
    status_dict: Dict[str, Any] = configurator.verify_prime_goal_status(agent)
    status = PrimeGoalStatus(**status_dict)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset Prime Goal configuration")
    return ActionResult(success=True, detail="Prime Goal configuration reset", status=status)


@app.get("/agent/supervisors", response_model=List[SupervisorAgent])
def get_supervisors() -> List[SupervisorAgent]:
    supervisors = []
    config_supervisors = configurator.prime_goal_config.get("supervisor_agents", {})
    for key, settings in config_supervisors.items():
        name = key.replace("_", " ").title()
        role = settings.get("role", "Supervisor Agent")
        optimization_level = settings.get("optimization_level", "maximum")
        supervisors.append(
            SupervisorAgent(
                id=key,
                name=name,
                role=role,
                optimization_level=optimization_level,
            )
        )
    return supervisors


@app.get("/agent/system-settings", response_model=SystemSettings)
def get_system_settings() -> SystemSettings:
    sys_settings = configurator.prime_goal_config.get("system_settings", {})
    return SystemSettings(
        global_optimizations=sys_settings.get("global_optimizations", {}),
        mcp_integration=sys_settings.get("mcp_integration", {}),
    )


@app.get("/agent/memory")
def get_memory() -> Dict[str, Any]:
    return {
        "memory": agent.memory,
        "stats": agent.get_memory_stats(),
    }


@app.post("/agent/command", response_model=CommandResponse)
async def send_command(payload: CommandRequest) -> CommandResponse:
    supervisors = configurator.prime_goal_config.get("supervisor_agents", {})
    if payload.supervisor_id not in supervisors:
        raise HTTPException(status_code=400, detail="Unknown supervisor_id")

    name = payload.supervisor_id.replace("_", " ").title()
    await _ensure_agent_initialized()

    command_text = payload.command.strip()

    # Use the supervisor orchestrator to choose an appropriate sub-agent.
    sub_agent = supervisor_orchestrator.select_sub_agent(command_text)

    # Give the shared agent clear context about which sub-agent is acting and why.
    query = (
        f"You are acting as the {sub_agent.role} sub-agent ({sub_agent.name}) "
        f"on behalf of supervisor '{name}'. "
        f"Interpret and execute the following command, explaining your plan and outcome:\n\n"
        f"{command_text}"
    )

    result = await agent.run_query(query)
    if result is None:
        content = command_text
    else:
        content = result.get("response", command_text)

    return CommandResponse(
        supervisor_id=payload.supervisor_id,
        supervisor_name=name,
        content=content,
        created_at=datetime.now().isoformat(),
    )


@app.post("/agent/query", response_model=AgentQueryResponse)
async def run_agent_query(payload: AgentQueryRequest) -> AgentQueryResponse:
    """Run a natural language query through the Prime Goal agent.

    This uses the OpenAI Assistant Agent with MCP integration under the hood.
    """

    await _ensure_agent_initialized()

    result = await agent.run_query(payload.query, thread_id=payload.thread_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Agent failed to process query")

    # result already has query, response, thread_id, timestamp
    return AgentQueryResponse(**result)


@app.post("/agent/supervisor/query", response_model=SupervisorQueryResponse)
async def run_supervisor_query(payload: AgentQueryRequest) -> SupervisorQueryResponse:
    """Run a query through the supervisor, returning plan and result.

    This wraps the shared OpenAI Assistant agent with lightweight planning
    metadata about which sub-agent handled the request.
    """

    await _ensure_agent_initialized()

    data = await supervisor_orchestrator.run_supervised(payload.query, thread_id=payload.thread_id)

    plan_dict = data.get("plan") or {}
    result_dict = data.get("result") or {}

    if not result_dict:
        raise HTTPException(status_code=500, detail="Supervisor failed to produce a result")

    plan = SupervisorPlan(**plan_dict)
    result = AgentQueryResponse(**result_dict)
    return SupervisorQueryResponse(plan=plan, result=result)


@app.get("/agent/tools", response_model=List[ToolDefinition])
def list_tools() -> List[ToolDefinition]:
    """Return a simple list of tools that this agent can use.

    This endpoint is intentionally descriptive rather than dynamic: it reflects
    the main MCP and built-in tools that Agent Private I is configured to call.
    """

    tools: List[ToolDefinition] = [
        ToolDefinition(
            name="web_search",
            description="Search the web for up-to-date information using the web search MCP router.",
            provider="MCP router",
            type="mcp",
            usage="The agent calls this automatically when it needs web data; no manual parameters required from the UI.",
        ),
        ToolDefinition(
            name="code_interpreter",
            description="Run Python code for data analysis, plotting, and file manipulation.",
            provider="OpenAI",
            type="built-in",
            usage="Used for calculations, CSV/JSON analysis, and scratchpad-style reasoning.",
        ),
        ToolDefinition(
            name="local_shell",
            description="Execute safe shell commands on the configured environment (for diagnostics and utilities).",
            provider="MCP local-shell",
            type="mcp",
            usage="Restricted to diagnostic commands; the agent decides when to invoke it.",
        ),
        ToolDefinition(
            name="file_search",
            description="Search project or knowledge base files via the file-search MCP tool.",
            provider="MCP file-search",
            type="mcp",
            usage="Used when the agent needs to look up information in your indexed repositories.",
        ),
        ToolDefinition(
            name="computer_use",
            description="High-level computer control for UI automation tasks.",
            provider="MCP computer-use",
            type="mcp",
            usage="Reserved for complex workflows that require interacting with desktop applications.",
        ),
    ]

    return tools


@app.get("/agent/mcp-tools", response_model=Dict[str, List[str]])
async def list_mcp_tools() -> Dict[str, List[str]]:
    """List real tools discovered from configured MCP servers.

    This complements /agent/tools by returning the actual tool names
    reported by each MCP server, when available.
    """

    await _ensure_agent_initialized()
    tools = await agent.list_available_tools()
    return tools


@app.post("/automation/webhooks", response_model=WebhookResponse)
async def create_webhook(payload: WebhookCreateRequest) -> WebhookResponse:
    await _ensure_automation_loaded()
    webhook_id = uuid4().hex
    created_at = datetime.now().isoformat()
    record = {
        "id": webhook_id,
        "url": str(payload.url),
        "secret": payload.secret,
        "enabled": payload.enabled,
        "created_at": created_at,
    }

    async with _automation_lock:
        _webhooks[webhook_id] = record

    await _save_automation_store()
    return WebhookResponse(
        id=webhook_id, url=payload.url, enabled=payload.enabled, created_at=created_at
    )


@app.get("/automation/webhooks")
async def list_webhooks() -> Dict[str, Any]:
    await _ensure_automation_loaded()
    async with _automation_lock:
        return {"webhooks": list(_webhooks.values())}


@app.delete("/automation/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str) -> Dict[str, Any]:
    await _ensure_automation_loaded()
    async with _automation_lock:
        existed = _webhooks.pop(webhook_id, None) is not None
        for s in _schedules.values():
            if isinstance(s.get("webhook_ids"), list) and webhook_id in s["webhook_ids"]:
                s["webhook_ids"] = [wid for wid in s["webhook_ids"] if wid != webhook_id]

    await _save_automation_store()
    _scheduler_wakeup.set()
    return {"deleted": existed}


@app.post("/automation/schedules", response_model=ScheduleResponse)
async def create_schedule(payload: ScheduleCreateRequest) -> ScheduleResponse:
    await _ensure_automation_loaded()

    if payload.interval_seconds < 1:
        raise HTTPException(status_code=400, detail="interval_seconds must be >= 1")

    if payload.kind not in {"agent_query", "web_search"}:
        raise HTTPException(status_code=400, detail="kind must be 'agent_query' or 'web_search'")

    schedule_id = uuid4().hex
    created_at = datetime.now().isoformat()
    now = time.time()
    record = {
        "id": schedule_id,
        "kind": payload.kind,
        "query": payload.query,
        "interval_seconds": int(payload.interval_seconds),
        "webhook_ids": list(payload.webhook_ids),
        "enabled": bool(payload.enabled),
        "created_at": created_at,
        "next_run_at": now + max(1, int(payload.interval_seconds)),
        "last_run_at": None,
        "last_run_ok": None,
        "last_run_error": None,
    }

    async with _automation_lock:
        _schedules[schedule_id] = record

    await _save_automation_store()
    _scheduler_wakeup.set()
    return ScheduleResponse(**record)


@app.get("/automation/schedules")
async def list_schedules() -> Dict[str, Any]:
    await _ensure_automation_loaded()
    async with _automation_lock:
        return {"schedules": list(_schedules.values())}


@app.post("/automation/schedules/{schedule_id}/run-now")
async def run_schedule_now(schedule_id: str) -> Dict[str, Any]:
    await _ensure_automation_loaded()
    async with _automation_lock:
        if schedule_id not in _schedules:
            raise HTTPException(status_code=404, detail="Unknown schedule_id")

    asyncio.create_task(_run_schedule(schedule_id))
    return {"queued": True, "schedule_id": schedule_id}


@app.post("/automation/web-search")
async def automation_web_search(payload: AgentQueryRequest) -> Dict[str, Any]:
    """Hard-coded web search via MCP (does not require OpenAI model access)."""

    await _ensure_mcp_initialized()
    return await _call_first_available_mcp_tool(
        ["tavily_search", "web_search"],
        {"query": payload.query},
    )


@app.post("/automation/filesystem/list")
async def automation_filesystem_list(payload: FilesystemPathRequest) -> Dict[str, Any]:
    """List a directory via MCP filesystem tools."""
    mapped = _map_path_for_docker_filesystem(payload.path)
    return await _call_first_available_mcp_tool(
        ["list_directory", "list_dir"],
        {"path": mapped},
    )


@app.post("/automation/filesystem/read")
async def automation_filesystem_read(payload: FilesystemPathRequest) -> Dict[str, Any]:
    """Read a file via MCP filesystem tools."""
    mapped = _map_path_for_docker_filesystem(payload.path)
    return await _call_first_available_mcp_tool(
        ["read_file", "read"],
        {"path": mapped},
    )


@app.post("/automation/filesystem/info")
async def automation_filesystem_info(payload: FilesystemPathRequest) -> Dict[str, Any]:
    """Get file/directory info via MCP filesystem tools."""
    mapped = _map_path_for_docker_filesystem(payload.path)
    return await _call_first_available_mcp_tool(
        ["get_file_info", "stat", "file_info", "get_file_stats"],
        {"path": mapped},
    )


@app.post("/automation/filesystem/search")
async def automation_filesystem_search(payload: FilesystemSearchRequest) -> Dict[str, Any]:
    """Search files under a directory via MCP filesystem tools."""
    mapped = _map_path_for_docker_filesystem(payload.path)
    return await _call_first_available_mcp_tool(
        ["search_files", "grep", "search"],
        {"path": mapped, "query": payload.query, "max_results": payload.max_results},
    )


@app.post("/automation/filesystem")
async def automation_filesystem(payload: FilesystemOpRequest) -> Dict[str, Any]:
    """Unified filesystem MCP endpoint.

    Body: {"op": "list"|"read"|"info"|"search", "path": "...", "query"?: "...", "max_results"?: 20}
    """

    op = (payload.op or "").strip().lower()
    if op == "list":
        tool_names = ["list_directory", "list_dir"]
    elif op == "read":
        tool_names = ["read_file", "read"]
    elif op == "info":
        tool_names = ["get_file_info", "stat", "file_info", "get_file_stats"]
    elif op == "search":
        if not payload.query:
            raise HTTPException(status_code=400, detail="query is required when op=search")
        tool_names = ["search_files", "grep", "search"]
    else:
        raise HTTPException(status_code=400, detail="op must be one of: list, read, info, search")

    mapped = _map_path_for_docker_filesystem(payload.path)

    if op == "search":
        return await _call_first_available_mcp_tool(
            tool_names,
            {
                "path": mapped,
                "query": payload.query,
                "max_results": payload.max_results or 20,
            },
        )

    return await _call_first_available_mcp_tool(tool_names, {"path": mapped})


@app.post("/automation/run")
async def automation_run(payload: AutomationRunRequest) -> Dict[str, Any]:
    """Run a one-off automation (agent query or web search), then POST to webhooks."""

    await _ensure_automation_loaded()
    kind = payload.kind
    if kind not in {"agent_query", "web_search"}:
        raise HTTPException(status_code=400, detail="kind must be 'agent_query' or 'web_search'")

    run_id = uuid4().hex
    started_at = time.time()
    output: Dict[str, Any] = {
        "run_id": run_id,
        "kind": kind,
        "query": payload.query,
        "started_at": started_at,
    }

    if kind == "web_search":
        output["search"] = await _call_first_available_mcp_tool(
            ["tavily_search", "web_search"],
            {"query": payload.query},
        )
    else:
        await _ensure_agent_initialized()
        agent_result = await agent.run_query(payload.query)
        if agent_result is None:
            raise HTTPException(status_code=500, detail="Agent failed to process query")
        output["agent"] = agent_result

    deliveries: Dict[str, Any] = {}
    async with _automation_lock:
        targets = [
            (wid, _webhooks.get(wid))
            for wid in payload.webhook_ids
            if isinstance(wid, str) and _webhooks.get(wid)
        ]

    for wid, wh in targets:
        if not wh or not wh.get("enabled", True):
            deliveries[wid] = {"ok": False, "error": "Webhook disabled or missing"}
            continue
        try:
            deliveries[wid] = await _dispatch_to_webhook(wh, output)
        except Exception as e:
            deliveries[wid] = {"ok": False, "error": f"{type(e).__name__}: {e}"}

    output["deliveries"] = deliveries
    output["finished_at"] = time.time()
    output["duration_seconds"] = max(0.0, output["finished_at"] - started_at)
    return output
