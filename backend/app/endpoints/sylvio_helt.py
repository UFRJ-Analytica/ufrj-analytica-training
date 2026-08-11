import sqlite3
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_connection

router = APIRouter(prefix="/sylvio-helt", tags=["sylvio_helt"])


@router.get("/status")
def status():
    return {"status": "ok"}


class KPIsResponse(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: int
    municipio_mais_populoso: str


@router.get("/kpis", response_model=KPIsResponse)
def get_kpis():
    db = get_connection()
    db.row_factory = sqlite3.Row

    total_municipios = db.execute("SELECT COUNT(*) AS c FROM municipios").fetchone()["c"]
    total_estados = db.execute("SELECT COUNT(*) AS c FROM estados").fetchone()["c"]

    populacao_total = db.execute(
        "SELECT SUM(valor) AS s FROM fato_indicador_municipal WHERE id_indicador = 1"
    ).fetchone()["s"]

    ano_referencia = db.execute(
        "SELECT ano FROM fato_indicador_municipal WHERE id_indicador = 1 LIMIT 1"
    ).fetchone()["ano"]

    mais_populoso = db.execute(
        """
        SELECT m.nome_municipio
        FROM municipios m
        JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
        WHERE f.id_indicador = 1
        ORDER BY f.valor DESC
        LIMIT 1
        """
    ).fetchone()

    return KPIsResponse(
        total_municipios=total_municipios,
        total_estados=total_estados,
        populacao_total=int(populacao_total),
        ano_referencia=ano_referencia,
        municipio_mais_populoso=mais_populoso["nome_municipio"],
    )


class TopMunicipioItem(BaseModel):
    id_municipio: int
    nome_municipio: str
    populacao: int
    sigla_uf: str


@router.get("/top-municipios", response_model=List[TopMunicipioItem])
def get_top_municipios(n: int = 10):
    db = get_connection()
    db.row_factory = sqlite3.Row

    rows = db.execute(
        """
        SELECT m.id_municipio, m.nome_municipio, f.valor AS populacao, e.sigla_uf
        FROM municipios m
        JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE f.id_indicador = 1
        ORDER BY f.valor DESC
        LIMIT ?
        """,
        (n,),
    ).fetchall()

    return [TopMunicipioItem(**dict(r)) for r in rows]


class PopulacaoRegiaoItem(BaseModel):
    id_regiao: int
    nome_regiao: str
    populacao_total: int


@router.get("/populacao-por-regiao", response_model=List[PopulacaoRegiaoItem])
def get_populacao_por_regiao():
    db = get_connection()
    db.row_factory = sqlite3.Row

    rows = db.execute(
        """
        SELECT r.id_regiao, r.nome_regiao, SUM(f.valor) AS populacao_total
        FROM fato_indicador_municipal f
        JOIN municipios m ON m.id_municipio = f.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE f.id_indicador = 1
        GROUP BY r.id_regiao, r.nome_regiao
        ORDER BY populacao_total DESC
        """
    ).fetchall()

    return [PopulacaoRegiaoItem(**dict(r)) for r in rows]


class PopulacaoEstadoItem(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    populacao_total: int


@router.get("/populacao-por-estado", response_model=List[PopulacaoEstadoItem])
def get_populacao_por_estado(id_regiao: int = None):
    db = get_connection()
    db.row_factory = sqlite3.Row

    rows = db.execute(
        """
        SELECT e.id_uf, e.sigla_uf, e.nome_uf, SUM(f.valor) AS populacao_total
        FROM fato_indicador_municipal f
        JOIN municipios m ON m.id_municipio = f.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE f.id_indicador = 1
          AND (? IS NULL OR e.id_regiao = ?)
        GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
        ORDER BY populacao_total DESC
        """,
        (id_regiao, id_regiao),
    ).fetchall()

    return [PopulacaoEstadoItem(**dict(r)) for r in rows]


class DistribuicaoItem(BaseModel):
    id_municipio: int
    nome_municipio: str
    populacao: int


@router.get("/distribuicao-populacao", response_model=List[DistribuicaoItem])
def get_distribuicao_populacao():
    db = get_connection()
    db.row_factory = sqlite3.Row

    rows = db.execute(
        """
        SELECT m.id_municipio, m.nome_municipio, f.valor AS populacao
        FROM municipios m
        JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
        WHERE f.id_indicador = 1
        """
    ).fetchall()

    return [DistribuicaoItem(**dict(r)) for r in rows]


class DispersaoEstadoItem(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_regiao: str
    qtd_municipios: int
    populacao_media: float


@router.get("/dispersao-estados", response_model=List[DispersaoEstadoItem])
def get_dispersao_estados():
    db = get_connection()
    db.row_factory = sqlite3.Row

    rows = db.execute(
        """
        SELECT e.id_uf, e.sigla_uf, r.nome_regiao,
               COUNT(m.id_municipio) AS qtd_municipios,
               AVG(f.valor) AS populacao_media
        FROM municipios m
        JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE f.id_indicador = 1
        GROUP BY e.id_uf, e.sigla_uf, r.nome_regiao
        """
    ).fetchall()

    return [DispersaoEstadoItem(**dict(r)) for r in rows]


class HeatmapCell(BaseModel):
    nome_regiao: str
    porte: str
    qtd_municipios: int


@router.get("/heatmap-regiao-porte", response_model=List[HeatmapCell])
def get_heatmap_regiao_porte():
    db = get_connection()
    db.row_factory = sqlite3.Row

    limite_pequeno = 20000
    limite_medio = 100000

    rows = db.execute(
        """
        SELECT
            r.nome_regiao,
            CASE
                WHEN f.valor < ? THEN 'pequeno'
                WHEN f.valor < ? THEN 'medio'
                ELSE 'grande'
            END AS porte,
            COUNT(*) AS qtd_municipios
        FROM fato_indicador_municipal f
        JOIN municipios m ON m.id_municipio = f.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE f.id_indicador = 1
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao, porte
        """,
        (limite_pequeno, limite_medio),
    ).fetchall()

    return [HeatmapCell(**dict(r)) for r in rows]


# CRUD de Município

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioUpdate(BaseModel):
    nome_municipio: Optional[str] = None
    id_uf: Optional[int] = None
    populacao: Optional[int] = None


class MunicipioResponse(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int


@router.get("/municipios/{id_municipio}", response_model=MunicipioResponse)
def get_municipio(id_municipio: int):
    db = get_connection()
    db.row_factory = sqlite3.Row

    row = db.execute(
        """
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, f.valor AS populacao
        FROM municipios m
        JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
        WHERE f.id_indicador = 1 AND m.id_municipio = ?
        """,
        (id_municipio,),
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return MunicipioResponse(**dict(row))


@router.post("/municipios", response_model=MunicipioResponse, status_code=201)
def create_municipio(payload: MunicipioCreate):
    db = get_connection()

    novo_id = db.execute(
        "SELECT COALESCE(MAX(id_municipio), 0) + 1 AS novo_id FROM municipios"
    ).fetchone()[0]

    db.execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, payload.nome_municipio, payload.id_uf),
    )
    db.execute(
        "INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor) VALUES (?, 1, 2025, ?)",
        (novo_id, payload.populacao),
    )
    db.commit()

    return MunicipioResponse(
        id_municipio=novo_id,
        nome_municipio=payload.nome_municipio,
        id_uf=payload.id_uf,
        populacao=payload.populacao,
    )


@router.put("/municipios/{id_municipio}", response_model=MunicipioResponse)
def update_municipio(id_municipio: int, payload: MunicipioUpdate):
    db = get_connection()
    db.row_factory = sqlite3.Row

    existente = db.execute(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)
    ).fetchone()
    if existente is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    if payload.nome_municipio is not None:
        db.execute(
            "UPDATE municipios SET nome_municipio = ? WHERE id_municipio = ?",
            (payload.nome_municipio, id_municipio),
        )
    if payload.id_uf is not None:
        db.execute(
            "UPDATE municipios SET id_uf = ? WHERE id_municipio = ?",
            (payload.id_uf, id_municipio),
        )
    if payload.populacao is not None:
        db.execute(
            "UPDATE fato_indicador_municipal SET valor = ? WHERE id_municipio = ? AND id_indicador = 1",
            (payload.populacao, id_municipio),
        )
    db.commit()

    row = db.execute(
        """
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, f.valor AS populacao
        FROM municipios m
        JOIN fato_indicador_municipal f ON f.id_municipio = m.id_municipio
        WHERE f.id_indicador = 1 AND m.id_municipio = ?
        """,
        (id_municipio,),
    ).fetchone()

    return MunicipioResponse(**dict(row))


@router.delete("/municipios/{id_municipio}", status_code=204)
def delete_municipio(id_municipio: int):
    db = get_connection()

    existente = db.execute(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)
    ).fetchone()
    if existente is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    db.execute(
        "DELETE FROM fato_indicador_municipal WHERE id_municipio = ? AND id_indicador = 1",
        (id_municipio,),
    )
    db.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    db.commit()


# CRUD de Cadastro

def _criar_tabela_cadastro():
    db = get_connection()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS cadastro_gestor (
            id_cadastro INTEGER PRIMARY KEY AUTOINCREMENT,
            id_municipio INTEGER NOT NULL,
            status TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            observacao TEXT,
            responsavel TEXT,
            FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
        )
        """
    )
    db.commit()


_criar_tabela_cadastro()


class CadastroCreate(BaseModel):
    id_municipio: int
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


class CadastroUpdate(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


class CadastroResponse(BaseModel):
    id_cadastro: int
    id_municipio: int
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


@router.get("/cadastro", response_model=List[CadastroResponse])
def list_cadastro(id_municipio: int = None):
    db = get_connection()
    db.row_factory = sqlite3.Row

    if id_municipio is not None:
        rows = db.execute(
            "SELECT * FROM cadastro_gestor WHERE id_municipio = ?", (id_municipio,)
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM cadastro_gestor").fetchall()

    return [CadastroResponse(**dict(r)) for r in rows]


@router.post("/cadastro", response_model=CadastroResponse, status_code=201)
def create_cadastro(payload: CadastroCreate):
    db = get_connection()

    municipio_existe = db.execute(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?",
        (payload.id_municipio,),
    ).fetchone()
    if municipio_existe is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    cursor = db.execute(
        """
        INSERT INTO cadastro_gestor (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
        """,
        (payload.id_municipio, payload.status, payload.prioridade, payload.observacao, payload.responsavel),
    )
    db.commit()

    return CadastroResponse(id_cadastro=cursor.lastrowid, **payload.model_dump())


@router.put("/cadastro/{id_cadastro}", response_model=CadastroResponse)
def update_cadastro(id_cadastro: int, payload: CadastroUpdate):
    db = get_connection()
    db.row_factory = sqlite3.Row

    existente = db.execute(
        "SELECT * FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,)
    ).fetchone()
    if existente is None:
        raise HTTPException(status_code=404, detail="Registro de cadastro não encontrado")

    campos = payload.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        db.execute(
            f"UPDATE cadastro_gestor SET {campo} = ? WHERE id_cadastro = ?",
            (valor, id_cadastro),
        )
    db.commit()

    row = db.execute(
        "SELECT * FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,)
    ).fetchone()
    return CadastroResponse(**dict(row))


@router.delete("/cadastro/{id_cadastro}", status_code=204)
def delete_cadastro(id_cadastro: int):
    db = get_connection()

    existente = db.execute(
        "SELECT id_cadastro FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,)
    ).fetchone()
    if existente is None:
        raise HTTPException(status_code=404, detail="Registro de cadastro não encontrado")

    db.execute("DELETE FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,))
    db.commit()