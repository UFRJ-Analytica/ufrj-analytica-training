import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()

    try:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> None:
    conn = get_connection()

    try:
        conn.execute(sql, params)
        conn.commit()

    finally:
        conn.close()