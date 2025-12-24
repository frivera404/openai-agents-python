from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    """Run the Agent Private I Prime Goal configuration flow.

    This reuses the existing test script so you can invoke the
    "launch" via a simple CLI command without duplicating logic.
    """

    project_root = Path(__file__).resolve().parents[2]
    script_path = project_root / "test_agent_private_i.py"
    runpy.run_path(str(script_path), run_name="__main__")


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
