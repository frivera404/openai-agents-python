import inspect

from examples.hosted_mcp import connectors


def test_main_is_async_callable() -> None:
    """Sanity check: `main` exists and is an async function (no network run)."""
    assert hasattr(connectors, "main")
    assert inspect.iscoroutinefunction(connectors.main)
