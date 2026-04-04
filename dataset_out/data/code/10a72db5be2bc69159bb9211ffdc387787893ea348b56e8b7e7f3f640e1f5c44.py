import pytest

from examples.basic.stream_items import how_many_jokes


def _unwrap_callable(obj):
    if callable(obj):
        return obj
    for attr in ("__wrapped__", "func", "fn", "callable"):
        if hasattr(obj, attr):
            candidate = getattr(obj, attr)
            if callable(candidate):
                return candidate
    return None


def test_how_many_jokes_in_range() -> None:
    """Ensure the example tool returns a value in the expected range."""
    func = _unwrap_callable(how_many_jokes)
    if func is None:
        pytest.skip("Could not find underlying callable for function_tool-wrapped object")

    for _ in range(50):
        n = func()
        assert isinstance(n, int)
        assert 1 <= n <= 10
