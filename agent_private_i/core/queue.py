import json
import time
from typing import Optional

from agent_private_i.core.models import Task


class InMemoryQueue:
    def __init__(self):
        self._items = []

    def enqueue(self, task: Task):
        payload = json.loads(json.dumps(task, default=lambda o: o.__dict__))
        self._items.insert(0, payload)

    def dequeue(self, block_seconds: int = 1) -> Optional[dict]:
        deadline = time.time() + block_seconds
        while time.time() < deadline:
            if self._items:
                return self._items.pop()
            time.sleep(0.1)
        return None


class RedisQueue:
    def __init__(self, url: str = "redis://localhost:6379/0", key: str = "tasks:queue"):
        try:
            import redis
        except Exception as err:
            raise RuntimeError("redis package required for RedisQueue") from err
        self.r = redis.from_url(url, decode_responses=True)
        self.key = key

    def enqueue(self, task: Task):
        payload = json.dumps(task, default=lambda o: o.__dict__)
        self.r.lpush(self.key, payload)

    def dequeue(self, block_seconds: int = 5) -> Optional[dict]:
        item = self.r.brpop(self.key, timeout=block_seconds)
        if not item:
            return None
        _, payload = item
        return json.loads(payload)
