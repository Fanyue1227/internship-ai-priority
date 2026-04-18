import sqlite3
from pathlib import Path


# Project root: Python/internship-ai-priority
BASE_DIR = Path(__file__).resolve().parents[1]

# Main SQLite database. All app data lives under data/.
DB_PATH = BASE_DIR / "data" / "app.db"


def get_connection():
    """Create a SQLite connection whose rows can be accessed by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
