import json
import logging
import os
from datetime import datetime

LOG_PATH = os.environ.get("AGENTS_LOG_PATH", "agent_system.log")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_system")


def log_event(event: dict):
    event = dict(event)
    event.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
    # remove any sensitive keys if present
    event.pop("secret", None)
    line = json.dumps(event)
    logger.info(line)
    try:
        with open(LOG_PATH, "a", encoding="utf8") as fh:
            fh.write(line + "\n")
    except Exception:
        logger.exception("failed to write log")
