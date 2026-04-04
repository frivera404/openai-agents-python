#!/usr/bin/env python3
"""
Example runner for the `ChatAgent` workflow demonstrating a short scripted
conversation that exercises the design → materials → laser → qc → finish flow.
"""
import json
import sys
import pathlib

# Ensure repository root is on sys.path when running this script directly.
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from examples.agents.chat_agent import create_agent


def main() -> None:
    agent = create_agent()

    steps = [
        "Create a design for a rectangular nameplate with 'Hello' text",
        "Prepare materials: 2 sheets of birch",
        "Run the laser job",
        "Perform QC check",
        "Finish and package",
    ]

    results = []
    for s in steps:
        out = agent.handle_message(s)
        print("USER:", s)
        print("AGENT:", json.dumps(out, indent=2, ensure_ascii=False))
        results.append({"input": s, "output": out})

    # Save combined run for inspection
    with open("chat_workflow_run.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Saved chat_workflow_run.json")


if __name__ == "__main__":
    main()
