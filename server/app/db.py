import sqlite3
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, db_path: str, cache_size: int = 128):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self.cache_size = cache_size
        self.history_cache: OrderedDict[str, List[Dict[str, str]]] = OrderedDict()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    title TEXT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )

    def ensure_session(self, session_id: str) -> None:
        now = utc_now()
        with self.lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions(id, created_at, updated_at, title)
                VALUES (?, ?, ?, NULL)
                ON CONFLICT(id) DO NOTHING
                """,
                (session_id, now, now),
            )

    def touch_session(self, session_id: str) -> None:
        with self.lock, self._connect() as conn:
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (utc_now(), session_id))

    def add_message(self, session_id: str, role: str, content: str) -> None:
        created_at = utc_now()
        with self.lock, self._connect() as conn:
            conn.execute(
                "INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, created_at),
            )
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (created_at, session_id))

        if session_id in self.history_cache:
            self.history_cache[session_id].append({"role": role, "content": content, "created_at": created_at})
            self.history_cache.move_to_end(session_id)

    def list_sessions(self) -> List[Dict[str, object]]:
        query = """
            SELECT s.id, s.title, s.updated_at, COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC
        """
        with self.lock, self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        if session_id in self.history_cache:
            self.history_cache.move_to_end(session_id)
            return self.history_cache[session_id]

        with self.lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()

        messages = [dict(row) for row in rows]
        self.history_cache[session_id] = messages
        if len(self.history_cache) > self.cache_size:
            self.history_cache.popitem(last=False)
        return messages

    def get_context_messages(self, session_id: str, context_turns: int) -> List[Dict[str, str]]:
        rows = self.get_messages(session_id)
        limit = max(context_turns * 2, 0)
        slice_rows = rows[-limit:] if limit else rows
        return [{"role": m["role"], "content": m["content"]} for m in slice_rows]

    def reset_session_messages(self, session_id: str) -> None:
        with self.lock, self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (utc_now(), session_id))
        self.history_cache.pop(session_id, None)

    def set_title(self, session_id: str, title: Optional[str]) -> None:
        with self.lock, self._connect() as conn:
            conn.execute("UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?", (title, utc_now(), session_id))
