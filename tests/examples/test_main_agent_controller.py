"""Smoke tests for the main agent controller example."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from examples.main_agent_controller import gpt_cli


def test_attach_files_reads_contents() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        file_path = Path(tmp) / "notes.txt"
        file_path.write_text("hello")
        attachments = gpt_cli.attach_files([str(file_path)])
        assert attachments, "Expected one attachment."
        payload = attachments[0]["content"]
        assert "notes.txt" in payload
        assert "hello" in payload


def test_run_tool_call_ping() -> None:
    result = gpt_cli.run_tool_call("ping", json.dumps({"message": "hi"}))
    payload = json.loads(result)
    assert payload["pong"] is True
    assert payload["echo"] == "hi"


def test_call_openai_missing_key_exits(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    try:
        gpt_cli.call_openai([], model="foo", stream=False)
    except SystemExit as exc:
        assert exc.code == 1
    else:  # pragma: no cover
        raise AssertionError("SystemExit was not raised.")
