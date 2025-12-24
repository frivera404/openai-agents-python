import pytest

import json
import asyncio

from src.agents.ctdatenight_agents import fetch_url, FINAL_SETTINGS
from src.agents.supervisor.orchestrator import SupervisorOrchestrator


class FakeResp:
    def __init__(self, url, status_code=200, headers=None, encoding="utf-8", history=None, content=b""):
        self.url = url
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "text/html"}
        self.encoding = encoding
        self.history = history or []
        self._content = content

    def iter_content(self, chunk_size=8192):
        yield self._content

    def close(self):
        return None


class FakeSession:
    def __init__(self, resp: FakeResp):
        self._resp = resp
        self.headers = {}

    def get(self, url, timeout=None, stream=None):
        return self._resp


def test_fetch_url_rejects_external_domain():
    # FunctionTool returns an error string on failure; call the async invoker.
    result = asyncio.run(fetch_url.on_invoke_tool(None, json.dumps({"url": "https://ctdatenight.com/"})))
    assert isinstance(result, str)
    assert "not on the allowed" in result or "allowed" in result


def test_fetch_url_redirects_to_disallowed_domain(monkeypatch):
    # history contains a redirect to a disallowed domain
    bad = FakeResp(url="https://evil.com/bad", status_code=200)
    good = FakeResp(url="https://ctdatenight.com/page", status_code=200, history=[bad], content=b"<html><body>ok</body></html>")
    monkeypatch.setattr("src.agents.ctdatenight_agents.requests.Session", lambda: FakeSession(good))
    result = asyncio.run(fetch_url.on_invoke_tool(None, json.dumps({"url": "https://ctdatenight.com/page"})))
    # Tool returns an error message string when runtime errors occur
    assert isinstance(result, str)
    assert "disallowed domain" in result or "Too many redirects" in result or "disallowed" in result


def test_fetch_url_success_strips_script(monkeypatch):
    html = b"<html><head><title>Test</title><script>alert(1)</script><style>p{}</style></head><body><h1>Hi</h1></body></html>"
    resp = FakeResp(url="https://ctdatenight.com/s", content=html)
    monkeypatch.setattr("src.agents.ctdatenight_agents.requests.Session", lambda: FakeSession(resp))
    res = asyncio.run(fetch_url.on_invoke_tool(None, json.dumps({"url": "https://ctdatenight.com/s"})))
    assert isinstance(res, dict)
    assert res["status_code"] == 200
    assert "<script" not in res["content"].lower()
    assert "<style" not in res["content"].lower()
    assert "Test" in res["content"]


def test_fetch_url_rewrites_links(monkeypatch):
    html = b"<html><body><a href=\"https://ctdatenight.com/offer\">Buy</a><a href=\"/signup\">Signup</a></body></html>"
    resp = FakeResp(url="https://ctdatenight.com/s", content=html)
    monkeypatch.setattr("src.agents.ctdatenight_agents.requests.Session", lambda: FakeSession(resp))
    res = asyncio.run(fetch_url.on_invoke_tool(None, json.dumps({"url": "https://ctdatenight.com/s"})))
    assert isinstance(res, dict)
    content = res["content"]
    # Original CTDateNight links should be replaced with redirect_url
    assert FINAL_SETTINGS["redirect_url"] in content
    assert "ctdatenight.com/offer" not in content
    assert "\"/signup\"" not in content


def test_supervisor_routing():
    orch = SupervisorOrchestrator(agent=None)
    assert orch.select_sub_agent("show me offers").id == "shopkeeper"
    assert orch.select_sub_agent("how do I sign up?").id == "shopkeeper"
    assert orch.select_sub_agent("I have a coupon question").id == "retention"
    assert orch.select_sub_agent("faq about bookings").id == "info"
    assert orch.select_sub_agent("hello there").id == "ui"

