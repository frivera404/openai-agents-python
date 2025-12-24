import json
import os
from typing import Optional


class FileStateStore:
    def __init__(self, path: str = ".agent_state"):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def _file(self, task_id: str) -> str:
        return os.path.join(self.path, f"{task_id}.json")

    def save(self, task_id: str, status: str, payload: dict):
        with open(self._file(task_id), "w", encoding="utf-8") as f:
            json.dump({"task_id": task_id, "status": status, "payload": payload}, f, indent=2)

    def load(self, task_id: str) -> Optional[dict]:
        p = self._file(task_id)
        if not os.path.exists(p):
            return None
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)


class PostgresStateStore:
    def __init__(self, dsn: str):
        try:
            import psycopg2
            from psycopg2.extras import Json
        except Exception:
            raise RuntimeError("psycopg2-binary required for PostgresStateStore")
        self.dsn = dsn
        self._init()

    def _init(self):
        import psycopg2
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                  task_id TEXT PRIMARY KEY,
                  status TEXT NOT NULL,
                  payload JSONB NOT NULL
                );
                """)
            conn.commit()

    def save(self, task_id: str, status: str, payload: dict):
        import psycopg2
        from psycopg2.extras import Json
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO tasks(task_id, status, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT(task_id) DO UPDATE SET
                  status=EXCLUDED.status,
                  payload=EXCLUDED.payload;
                """, (task_id, status, Json(payload)))
            conn.commit()

    def load(self, task_id: str):
        import psycopg2
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT payload FROM tasks WHERE task_id=%s", (task_id,))
                row = cur.fetchone()
                return row[0] if row else None
