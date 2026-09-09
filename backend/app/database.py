"""
Camada de acesso ao banco de dados (SQLite).

Este módulo concentra a lógica de conexão para que os endpoints não
precisem se preocupar em abrir/fechar conexões manualmente.
"""
import sqlite3
from pathlib import Path

# O database.db fica na raiz do repositório, um nível acima de "backend".
DB_PATH = "./dados/database.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão com o SQLite configurada para retornar dicts (Row)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Executa um SELECT e retorna uma lista de dicts."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def alter(sql: str, params: tuple = ()):
    """Executa um INSERT e retorna se foi bem sucessido"""
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
        return {"success": True, 'detail': ''}
    except Exception as e:
        return {"success": False, 'detail': ""}
    finally:
        conn.close()

