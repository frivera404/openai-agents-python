import asyncio
import pytest

from examples.basic.stream_function_call_args import write_file, simulate_streamed_function_call_args


def _unwrap_callable(obj):
    if callable(obj):
        return obj
    for attr in ("__wrapped__", "func", "fn", "callable"):
        if hasattr(obj, attr):
            candidate = getattr(obj, attr)
            if callable(candidate):
                return candidate
    return None


def test_write_file_returns_expected_string() -> None:
    func = _unwrap_callable(write_file)
    if func is None:
        pytest.skip("Could not find underlying callable for function_tool-wrapped object")
    res = func("a.txt", "abc")
    assert "File a.txt written" in res


def test_simulate_stream_assembles_args() -> None:
    async def _consume() -> tuple[str, str]:
        assembled = {"filename": "", "content": ""}
        finished = {"filename": False, "content": False}
        async for ev in simulate_streamed_function_call_args():
            if ev.get("type") != "function_call_arg_delta":
                continue
            arg = ev["arg"]
            assembled[arg] += ev["chunk"]
            if ev.get("final"):
                finished[arg] = True
            if all(finished.values()):
                return assembled["filename"], assembled["content"]
        return assembled["filename"], assembled["content"]

    filename, content = asyncio.run(_consume())
    assert filename.endswith("2024.txt")
    assert "This is the first line." in content
