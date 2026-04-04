#!/usr/bin/env python3
"""
MCP tools for a small engraving & laser-cutting workshop.

This exposes one tool per Agent from the sample schedule so you can
exercise the workflow as MCP tools over the streamable-http transport.
"""
from typing import Optional
import json
import os
import time

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Engraving Workshop Agents")


@mcp.tool()
def create_design(client_requirements: str, style: str = "standard") -> str:
    """Design Agent: produce a vector filename and short notes.

    This is a lightweight placeholder that writes a small SVG file and
    returns its path and a summary.
    """
    name = f"design_{int(time.time())}.svg"
    svg = f"<svg><!-- design style={style} --><text>{client_requirements}</text></svg>\n"
    path = os.path.join("./dataset_out", name)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        return json.dumps({"design_file": path, "notes": f"Style={style}; length={len(client_requirements)}"})
    except Exception as e:
        return f"ERROR: failed to create design file: {e}"


@mcp.tool()
def prepare_materials(material: str = "birch", sheets: int = 1) -> str:
    """Material Preparation Agent: reserve and prepare material and return batch id."""
    batch_id = f"batch_{material}_{int(time.time())}"
    # Placeholder actions: in a real setup this might check inventory, mark reserved.
    return json.dumps({"batch_id": batch_id, "material": material, "sheets": sheets})


@mcp.tool()
def run_laser_job(design_file: str, batch_id: str, test_run: bool = False) -> str:
    """Laser Operator Agent: simulate running the laser job and report status."""
    # Validate inputs simply
    if not os.path.exists(design_file):
        return f"ERROR: design file not found: {design_file}"
    job_id = f"job_{int(time.time())}"
    status = "test_ok" if test_run else "completed"
    # Simulate short processing
    time.sleep(0.2)
    return json.dumps({"job_id": job_id, "status": status, "design_file": design_file, "batch_id": batch_id})


@mcp.tool()
def qc_check(job_id: str, sample_file: Optional[str] = None) -> str:
    """Quality Control Agent: inspect results and return pass/fail and notes."""
    # This is a deterministic placeholder: odd job_id seconds -> fail (for variety)
    try:
        ts = int(job_id.split("_")[-1])
        passed = (ts % 2) == 0
    except Exception:
        passed = True
    notes = "All tolerances OK" if passed else "Minor burn; adjust power/settings"
    return json.dumps({"job_id": job_id, "passed": passed, "notes": notes, "sample": sample_file})


@mcp.tool()
def finish_and_package(job_id: str, finish_type: str = "oil", box_size: str = "medium") -> str:
    """Finishing & Packaging Agent: simulate finishing steps and return package id."""
    pkg_id = f"pkg_{int(time.time())}"
    # Simulate a small delay
    time.sleep(0.1)
    return json.dumps({"pkg_id": pkg_id, "job_id": job_id, "finish": finish_type, "box": box_size})


@mcp.tool()
def coordinator_overview() -> str:
    """Project Coordinator Agent: return the built-in schedule summary if available."""
    # Try to read orchestration_schedule.json produced by orchestrate_and_complete.py
    path = "orchestration_schedule.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                sched = json.load(f)
            return json.dumps({"schedule_source": path, "schedule": sched}, indent=2)
        except Exception as e:
            return f"ERROR: failed to read {path}: {e}"
    # Fallback: minimal inline summary
    summary = {
        "Design Agent": "Mon/Wed 09:00-11:00",
        "Material Preparation Agent": "Mon/Wed 11:00-13:00",
        "Laser Operator Agent": "Tue/Thu 09:00-12:00",
        "Quality Control Agent": "Tue/Thu 12:00-13:00",
        "Finishing & Packaging Agent": "Fri 09:00-12:00",
        "Project Coordinator Agent": "Daily 08:30-09:00",
    }
    return json.dumps({"schedule_source": "inline", "schedule": summary}, indent=2)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run Engraving Workshop MCP tools (streamable-http)")
    parser.add_argument("--stdio", action="store_true", help="Run over stdio transport")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3005)
    args = parser.parse_args()

    if args.stdio:
        print("Starting Engraving Workshop Agents server on stdio transport")
        mcp.run(transport="stdio")
    else:
        print("Starting Engraving Workshop Agents server on streamable-http transport")
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
