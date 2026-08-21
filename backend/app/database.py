"""
Camada de acesso ao banco de dados (SQLite).

Este módulo concentra a lógica de conexão para que os endpoints não
precisem se preocupar em abrir/fechar conexões manualmente.
"""
import sqlite3
from pathlib import Path

# O database.db fica na raiz do repositório, um nível acima de "backend".
DB_PATH = Path(__file__).resolve().parent.parent.parent / "database.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão com o SQLite configurada para retornar dicts (Row)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Executa comandos SQL."""
    conn = get_connection()

    try:
        cursor = conn.execute(sql, params)

        if cursor.description is not None:
            # SELECT
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        else:
            # INSERT, UPDATE ou DELETE
            conn.commit()
            return []

    finally:
        conn.close()
