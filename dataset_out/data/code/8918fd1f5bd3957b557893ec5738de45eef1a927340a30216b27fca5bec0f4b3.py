from __future__ import annotations

from typing import Any


async def runSupervisorQuery(body: dict[str, Any]) -> dict[str, Any]:
    """Stub implementation used by tests.

    The real implementation lives in the frontend TypeScript client
    (see ``frontend/src/api/agentApi.ts``) and talks to the HTTP
    Prime Goal API. In Python tests we only need the symbol to exist,
    not to perform real network I/O, so this placeholder raises if
    called.
    """

    raise RuntimeError(
        "runSupervisorQuery is a frontend helper and is not "
        "implemented in the Python test environment."
    )
