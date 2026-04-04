#!/usr/bin/env python3
"""Run a sample end-to-end flow against the engraving agents tools."""
import json
from examples.agents import engraving_agents as ea


def main() -> None:
    # 1) Design
    design = json.loads(ea.create_design("Logo for ACME, size 200x100", style="modern"))

    # 2) Prepare materials
    materials = json.loads(ea.prepare_materials("birch", sheets=2))

    # 3) Run laser (test run)
    run = json.loads(ea.run_laser_job(design["design_file"], materials["batch_id"], test_run=True))

    # 4) QC check
    qc = json.loads(ea.qc_check(run["job_id"]))

    # 5) Finish & package
    finish = json.loads(ea.finish_and_package(run["job_id"], finish_type="oil", box_size="small"))

    result = {"design": design, "materials": materials, "run": run, "qc": qc, "finish": finish}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
