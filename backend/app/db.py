from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import get_settings


_data_dir = get_settings().data_dir
_db_path = get_settings().db_path


def configure_database(data_dir: Path) -> None:
    """Point the app database at a specific data directory.

    Tests use this to isolate state. Production code uses the default data/
    directory under the project root.
    """
    global _data_dir, _db_path
    _data_dir = Path(data_dir)
    _db_path = _data_dir / "app.db"


def get_data_dir() -> Path:
    return _data_dir


def get_db_path() -> Path:
    return _db_path


def get_connection() -> sqlite3.Connection:
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                source_path TEXT NOT NULL,
                section TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS board_days (
                date TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                focus TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS board_day_rationale (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_date TEXT NOT NULL,
                content TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                FOREIGN KEY(day_date) REFERENCES board_days(date) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS board_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_date TEXT NOT NULL,
                task_key TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                eta TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL,
                FOREIGN KEY(day_date) REFERENCES board_days(date) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS board_task_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                step_type TEXT NOT NULL,
                content TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                FOREIGN KEY(task_id) REFERENCES board_tasks(id) ON DELETE CASCADE
            );
            """
        )
