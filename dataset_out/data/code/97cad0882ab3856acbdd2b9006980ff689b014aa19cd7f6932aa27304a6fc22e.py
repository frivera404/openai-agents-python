from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

import agents.http_prime_goal_api as api


def get_test_client() -> TestClient:
    return TestClient(api.app)


def test_list_tools_returns_core_tools() -> None:
    client = get_test_client()

    resp = client.get("/agent/tools")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    # Expect at least one core tool like web_search
    tool_names = {t["name"] for t in data}
    assert "web_search" in tool_names


def test_agent_query_uses_lazy_initialization_once(monkeypatch) -> None:
    calls: dict[str, int] = {"init": 0, "create": 0, "query": 0}

    async def fake_init_mcp() -> bool:  # type: ignore[return-type]
        calls["init"] += 1
        return True

    def fake_create_agent() -> bool:
        calls["create"] += 1
        return True

    async def fake_run_query(query: str, thread_id: str | None = None) -> dict[str, Any]:
        calls["query"] += 1
        return {
            "query": query,
            "response": "ok",
            "thread_id": thread_id,
            "timestamp": 123.0,
        }

    # Reset initialization flag so our test controls the lifecycle.
    monkeypatch.setattr(api, "_agent_initialized", False)
    monkeypatch.setattr(api.agent, "initialize_mcp_servers", fake_init_mcp)
    monkeypatch.setattr(api.agent, "create_agent", fake_create_agent)
    monkeypatch.setattr(api.agent, "run_query", fake_run_query)

    client = get_test_client()

    resp1 = client.post("/agent/query", json={"query": "first"})
    resp2 = client.post("/agent/query", json={"query": "second"})

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    # Lazy init should only run once even across multiple queries.
    assert calls["init"] == 1
    assert calls["create"] == 1
    assert calls["query"] == 2


def test_list_mcp_tools_uses_agent(monkeypatch) -> None:
    fake_tools: dict[str, list[str]] = {"local-mcp": ["web_search", "file_search"]}

    async def fake_init_mcp() -> bool:  # type: ignore[return-type]
        return True

    def fake_create_agent() -> bool:
        return True

    async def fake_list_available_tools() -> dict[str, list[str]]:
        return fake_tools

    # Force a fresh init for this test
    monkeypatch.setattr(api, "_agent_initialized", False)
    monkeypatch.setattr(api.agent, "initialize_mcp_servers", fake_init_mcp)
    monkeypatch.setattr(api.agent, "create_agent", fake_create_agent)
    monkeypatch.setattr(api.agent, "list_available_tools", fake_list_available_tools)

    client = get_test_client()

    resp = client.get("/agent/mcp-tools")
    assert resp.status_code == 200

    data = resp.json()
    assert data == fake_tools


def test_supervisor_query_returns_plan_and_result(monkeypatch) -> None:
    """Supervisor endpoint should return both plan metadata and agent result."""

    async def fake_run_supervised(query: str, thread_id: str | None = None) -> dict[str, Any]:
        return {
            "plan": {
                "selected_sub_agent_id": "research",
                "selected_sub_agent_name": "Research Agent",
                "selected_sub_agent_role": "Researcher",
                "selected_sub_agent_description": "Finds information.",
            },
            "result": {
                "query": query,
                "response": "ok",
                "thread_id": thread_id,
                "timestamp": 123.0,
            },
        }

    # Avoid triggering real initialization in tests.
    monkeypatch.setattr(api, "_agent_initialized", True)
    monkeypatch.setattr(api.supervisor_orchestrator, "run_supervised", fake_run_supervised)

    client = get_test_client()

    resp = client.post("/agent/supervisor/query", json={"query": "look up docs"})
    assert resp.status_code == 200

    data = resp.json()
    assert "plan" in data and "result" in data
    assert data["plan"]["selected_sub_agent_id"] == "research"
    assert data["result"]["response"] == "ok"


def test_command_with_deploy_routes_to_automation(monkeypatch) -> None:
    """Commands containing 'deploy' should be handled by the automation sub-agent."""

    # Provide a minimal supervisor config so the endpoint accepts the supervisor_id.
    fake_config = {
        "supervisor_agents": {
            "main_supervisor": {"role": "Supervisor Agent", "optimization_level": "maximum"}
        }
    }

    async def fake_run_query(query: str, thread_id: str | None = None) -> dict[str, Any]:
        # Expose the query so we can assert that automation context was injected.
        return {
            "query": query,
            "response": query,
            "thread_id": thread_id,
            "timestamp": 123.0,
        }

    monkeypatch.setattr(api, "_agent_initialized", True)
    monkeypatch.setattr(api, "configurator", api.configurator)
    api.configurator.prime_goal_config = fake_config
    monkeypatch.setattr(api.agent, "run_query", fake_run_query)

    client = get_test_client()

    resp = client.post(
        "/agent/command",
        json={"supervisor_id": "main_supervisor", "command": "deploy latest version"},
    )

    assert resp.status_code == 200
    data = resp.json()
    # The response echoes the underlying query string from fake_run_query.
    # Ensure that the automation sub-agent description is present in the prompt.
    assert "Automation Agent" in data["content"] or "Executor" in data["content"]
