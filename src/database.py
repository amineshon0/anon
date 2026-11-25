import secrets
import sqlite3
from pathlib import Path
from typing import Any


class Database:
    """Lightweight SQLite database manager for the anonymous messaging bot."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    username TEXT,
                    link_code TEXT UNIQUE NOT NULL,
                    is_accepting INTEGER NOT NULL DEFAULT 1,
                    custom_bio TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    reply_to_msg_id INTEGER,
                    msg_type TEXT NOT NULL DEFAULT 'text',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS blocks (
                    blocker_id INTEGER NOT NULL,
                    blocked_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (blocker_id, blocked_id)
                );
                """
            )

    @staticmethod
    def _generate_code() -> str:
        return secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:10]

    def get_or_create_user(
        self, user_id: int, full_name: str, username: str | None = None
    ) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE users SET full_name = ?, username = ? WHERE user_id = ?",
                    (full_name, username, user_id),
                )
                return dict(row)

            code = self._generate_code()
            while conn.execute(
                "SELECT 1 FROM users WHERE link_code = ?", (code,)
            ).fetchone():
                code = self._generate_code()

            conn.execute(
                """
                INSERT INTO users (user_id, full_name, username, link_code)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, full_name, username, code),
            )
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row)

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_user_by_code(self, link_code: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE link_code = ?", (link_code,)
            ).fetchone()
            return dict(row) if row else None

    def regenerate_link_code(self, user_id: int) -> str:
        with self._connect() as conn:
            code = self._generate_code()
            while conn.execute(
                "SELECT 1 FROM users WHERE link_code = ?", (code,)
            ).fetchone():
                code = self._generate_code()
            conn.execute(
                "UPDATE users SET link_code = ? WHERE user_id = ?", (code, user_id)
            )
            return code

    def toggle_accepting(self, user_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT is_accepting FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            new_val = 0 if (row and row["is_accepting"]) else 1
            conn.execute(
                "UPDATE users SET is_accepting = ? WHERE user_id = ?",
                (new_val, user_id),
            )
            return bool(new_val)

    def set_custom_bio(self, user_id: int, bio: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET custom_bio = ? WHERE user_id = ?",
                (bio.strip()[:200], user_id),
            )

    def save_message(
        self,
        sender_id: int,
        receiver_id: int,
        msg_type: str = "text",
        reply_to_msg_id: int | None = None,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (sender_id, receiver_id, reply_to_msg_id, msg_type)
                VALUES (?, ?, ?, ?)
                """,
                (sender_id, receiver_id, reply_to_msg_id, msg_type),
            )
            return int(cursor.lastrowid)

    def get_message(self, msg_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM messages WHERE id = ?", (msg_id,)
            ).fetchone()
            return dict(row) if row else None

    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO blocks (blocker_id, blocked_id)
                VALUES (?, ?)
                """,
                (blocker_id, blocked_id),
            )

    def is_blocked(self, blocker_id: int, blocked_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM blocks WHERE blocker_id = ? AND blocked_id = ?",
                (blocker_id, blocked_id),
            ).fetchone()
            return row is not None

    def unblock_all(self, blocker_id: int) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM blocks WHERE blocker_id = ?", (blocker_id,)
            )
            return cursor.rowcount

    def get_user_stats(self, user_id: int) -> dict[str, int]:
        with self._connect() as conn:
            received = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE receiver_id = ?", (user_id,)
            ).fetchone()[0]
            sent = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE sender_id = ?", (user_id,)
            ).fetchone()[0]
            blocked = conn.execute(
                "SELECT COUNT(*) FROM blocks WHERE blocker_id = ?", (user_id,)
            ).fetchone()[0]
            return {
                "received": received,
                "sent": sent,
                "blocked": blocked,
            }

    def get_global_stats(self) -> dict[str, int]:
        with self._connect() as conn:
            users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            return {"users": users, "messages": messages}
