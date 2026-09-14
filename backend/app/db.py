import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Database:
    """Small document repository; cross-document references are checked by the API."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("CREATE TABLE IF NOT EXISTS documents (collection TEXT NOT NULL, id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(collection, id))")
            conn.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def all(self, collection: str) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload FROM documents WHERE collection=? ORDER BY rowid DESC", (collection,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def get(self, collection: str, identifier: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute("SELECT payload FROM documents WHERE collection=? AND id=?", (collection, identifier)).fetchone()
        return json.loads(row[0]) if row else None

    def save(self, collection: str, payload: dict) -> dict:
        with self.connect() as conn:
            conn.execute("INSERT INTO documents VALUES (?, ?, ?) ON CONFLICT(collection,id) DO UPDATE SET payload=excluded.payload", (collection, payload["id"], json.dumps(payload, ensure_ascii=False)))
        return payload

    def snapshot(self) -> dict:
        with self.connect() as conn:
            rows = conn.execute("SELECT collection, payload FROM documents ORDER BY rowid DESC").fetchall()
        result = {"version": 1, "tracks": [], "entries": [], "sessions": []}
        for collection, payload in rows:
            result[collection].append(json.loads(payload))
        return result

    def merge(self, backup: dict) -> int:
        count = 0
        with self.connect() as conn:
            for collection in ("tracks", "entries", "sessions"):
                for item in backup[collection]:
                    result = conn.execute("INSERT OR IGNORE INTO documents VALUES (?, ?, ?)", (collection, item["id"], json.dumps(item, ensure_ascii=False)))
                    count += result.rowcount
        return count
