"""
Camada de acesso ao banco de dados (SQLite).

Este módulo concentra a lógica de conexão para que os endpoints não
precisem se preocupar em abrir/fechar conexões manualmente.
"""
import os
import shutil
import sqlite3
from pathlib import Path

# Banco "semente": vai dentro da imagem do backend (backend/database.db),
# copiado pelo Dockerfile junto com o resto do código. Usado tanto pra rodar
# localmente sem Docker quanto pra popular o volume na primeira vez que o
# container sobe.
SEED_DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def _resolve_db_path() -> Path:
    """
    Decide o caminho real do database.db:
    - se DATABASE_URL estiver definida (o compose.yaml define isso, apontando
      pro volume nomeado sqlite_data), usa esse caminho;
    - senão, usa o banco semente ao lado do código (rodando localmente, sem
      Docker).
    Se o caminho escolhido ainda não existir (ex.: volume vazio na primeira
    subida do container), copia o banco semente pra lá.
    """
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        db_path = Path(database_url.removeprefix("sqlite:///"))
    else:
        db_path = SEED_DB_PATH

    if not db_path.exists() and SEED_DB_PATH.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SEED_DB_PATH, db_path)

    return db_path


def _ensure_extra_tables(db_path: Path) -> None:
    """Cria tabelas que não vêm no database.db original (cadastro do gestor)."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS anotacoes_gestor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_municipio INTEGER NOT NULL,
                status TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                observacao TEXT,
                responsavel TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


DB_PATH = _resolve_db_path()
_ensure_extra_tables(DB_PATH)


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
