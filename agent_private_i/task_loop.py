"""Task loop for Agent Private I.

Polls Redis `tasks:queue` (preferred) or a local directory `./local_tasks/` for JSON tasks,
then runs them through the orchestrator (from `agent_private_i.app.build_system`).

Usage:
  uv run python -m agent_private_i.task_loop

Environment:
  REDIS_URL - redis://... if set the loop will use RedisQueue; otherwise falls back to local files.
"""
import json
import os
import time
import logging
from pathlib import Path

from agent_private_i.app import build_system

try:
    from agent_private_i.core.queue import RedisQueue
except Exception:
    RedisQueue = None


logging.basicConfig(level=logging.INFO)


def process_payload(orch, payload):
    try:
        logging.info(f"Running task {payload.get('task_id')}")
        result = orch.run_task(payload)
        logging.info(f"Task {result.get('task_id')} finished: {result.get('status')}")
        return result
    except Exception as e:
        logging.exception("Task run failed")
        return None


def redis_loop(orch, redis_url: str):
    if RedisQueue is None:
        logging.error("RedisQueue not available (missing python redis package)")
        return

    q = RedisQueue(url=redis_url)
    logging.info("Listening to Redis queue 'tasks:queue'")
    while True:
        payload = q.dequeue(block_seconds=5)
        if not payload:
            time.sleep(0.2)
            continue
        # payload already a dict
        process_payload(orch, payload)


def local_loop(orch, tasks_dir: Path):
    tasks_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = tasks_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    logging.info(f"Watching local tasks in {tasks_dir}")
    while True:
        files = sorted(tasks_dir.glob("*.json"))
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    payload = json.load(fh)
                result = process_payload(orch, payload)
                # move file to processed
                target = processed_dir / f.name
                try:
                    # atomic replace where possible
                    f.replace(target)
                except FileNotFoundError:
                    # another process may have removed/moved the file; log and continue
                    logging.warning("Task file disappeared before move: %s", f)
                except Exception:
                    # fallback: try copy + unlink
                    try:
                        import shutil
                        shutil.copy2(str(f), str(target))
                        if f.exists():
                            f.unlink()
                    except Exception:
                        logging.exception("Failed to move processed task file %s", f)
            except Exception:
                logging.exception(f"Failed to process {f}")
        time.sleep(1)


def main():
    orch, store = build_system()

    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            redis_loop(orch, redis_url)
            return
        except Exception:
            logging.exception("Redis loop failed, falling back to local loop")

    # fallback: local directory
    local_dir = Path(os.environ.get("LOCAL_TASK_DIR", "local_tasks"))
    local_loop(orch, local_dir)


if __name__ == "__main__":
    main()
