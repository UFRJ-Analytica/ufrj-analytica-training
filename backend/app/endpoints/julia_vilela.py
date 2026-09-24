

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from app.database import query, execute
from app import schemas

router = APIRouter(prefix="/julia-vilela", tags=["julia_vilela"])


# ---------------------------------------------------------------------------
# Helper: um único registro (query() devolve lista de dicts).
# ---------------------------------------------------------------------------
def query_one(sql: str, params: tuple = ()) -> Optional[dict]:
    rows = query(sql, params)
    return rows[0] if rows else None


# ===========================================================================
#  Garante a tabela de cadastro do gestor (já existe no banco, mas
#  criamos com IF NOT EXISTS para o código rodar em qualquer cópia).
# ===========================================================================
def init_cadastro_table() -> None:
    execute(
        """
        CREATE TABLE IF NOT EXISTS acompanhamento_gestor (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            id_municipio  INTEGER NOT NULL,
            status        TEXT    NOT NULL DEFAULT 'monitorando',
            prioridade    TEXT    NOT NULL DEFAULT 'media',
            observacao    TEXT,
            responsavel   TEXT,
            atualizado_em TEXT    DEFAULT (datetime('now'))
        )
        """
    )


init_cadastro_table()


# ###########################################################################
#  PARTE 1A — CONSULTA E ANÁLISE
# ###########################################################################

@router.get("/status")
def status():
    return {"status": "ok"}


# ---- KPIs -----------------------------------------------------------------
@router.get("/kpis", response_model=schemas.KPIs)
def kpis():
    total_municipios = query_one("SELECT COUNT(*) AS n FROM municipios")["n"]
    total_estados = query_one("SELECT COUNT(*) AS n FROM estados")["n"]
    populacao_total = query_one(
        "SELECT COALESCE(SUM(valor), 0) AS total FROM populacao_municipal"
    )["total"]
    ano_ref = query_one("SELECT MAX(ano) AS ano FROM populacao_municipal")["ano"]

    mais_populoso = query_one(
        """
        SELECT m.nome_municipio AS municipio,
               e.sigla_uf       AS uf,
               p.valor          AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados   e ON e.id_uf         = m.id_uf
        ORDER BY p.valor DESC
        LIMIT 1
        """
    )

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": ano_ref,
        "municipio_mais_populoso": mais_populoso,
    }


# ---- Top N municípios -----------------------------------------------------
@router.get("/top-municipios", response_model=List[schemas.MunicipioPopulacao])
def top_municipios(n: int = Query(10, ge=1, le=100)):
    return query(
        """
        SELECT m.id_municipio   AS id_municipio,
               m.nome_municipio AS municipio,
               e.sigla_uf       AS uf,
               p.valor          AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados   e ON e.id_uf         = m.id_uf
        ORDER BY p.valor DESC
        LIMIT ?
        """,
        (n,),
    )


# ---- População por região -------------------------------------------------
@router.get("/populacao-por-regiao", response_model=List[schemas.RegiaoPopulacao])
def populacao_por_regiao():
    return query(
        """
        SELECT r.nome_regiao AS regiao,
               COALESCE(SUM(p.valor), 0) AS populacao
        FROM regioes r
        JOIN estados    e ON e.id_regiao    = r.id_regiao
        JOIN municipios m ON m.id_uf         = e.id_uf
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        GROUP BY r.id_regiao, r.nome_regiao
        ORDER BY populacao DESC
        """
    )


# ---- População por estado (filtro opcional por região) --------------------
@router.get("/populacao-por-estado", response_model=List[schemas.EstadoPopulacao])
def populacao_por_estado(regiao: Optional[str] = Query(None)):
    sql = """
        SELECT e.sigla_uf    AS uf,
               e.nome_uf     AS estado,
               r.nome_regiao AS regiao,
               COALESCE(SUM(p.valor), 0) AS populacao
        FROM estados e
        JOIN regioes    r ON r.id_regiao   = e.id_regiao
        JOIN municipios m ON m.id_uf        = e.id_uf
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
    """
    params: tuple = ()
    if regiao:
        sql += " WHERE r.nome_regiao = ? "
        params = (regiao,)
    sql += " GROUP BY e.id_uf, e.sigla_uf, e.nome_uf, r.nome_regiao ORDER BY populacao DESC"
    return query(sql, params)


# ---- Distribuição da população --------------------------------------------
@router.get("/distribuicao-populacao", response_model=List[int])
def distribuicao_populacao():
    rows = query("SELECT valor FROM populacao_municipal ORDER BY valor")
    return [r["valor"] for r in rows]


# ---- Dispersão: qtd municípios x população média por estado ---------------
@router.get("/dispersao-estados", response_model=List[schemas.DispersaoEstado])
def dispersao_estados():
    return query(
        """
        SELECT e.sigla_uf    AS uf,
               e.nome_uf      AS estado,
               r.nome_regiao  AS regiao,
               COUNT(m.id_municipio)      AS qtd_municipios,
               COALESCE(AVG(p.valor), 0)  AS populacao_media
        FROM estados e
        JOIN regioes    r ON r.id_regiao   = e.id_regiao
        JOIN municipios m ON m.id_uf        = e.id_uf
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        GROUP BY e.id_uf, e.sigla_uf, e.nome_uf, r.nome_regiao
        ORDER BY qtd_municipios DESC
        """
    )


# ---- Heatmap: região x porte ----------------------------------------------
# pequeno < 20.000 | medio 20.000–100.000 | grande > 100.000
@router.get("/heatmap-regiao-porte", response_model=List[schemas.RegiaoPorte])
def heatmap_regiao_porte():
    return query(
        """
        SELECT r.nome_regiao AS regiao,
               CASE
                   WHEN p.valor < 20000  THEN 'pequeno'
                   WHEN p.valor < 100000 THEN 'medio'
                   ELSE 'grande'
               END AS porte,
               COUNT(*) AS quantidade
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados   e ON e.id_uf         = m.id_uf
        JOIN regioes   r ON r.id_regiao     = e.id_regiao
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao, porte
        """
    )


# ###########################################################################
#  PARTE 1B — MUNICÍPIO (dados básicos)
# ###########################################################################

@router.get("/municipios", response_model=List[schemas.MunicipioPopulacao])
def listar_municipios(
    q: Optional[str] = Query(None, description="busca por nome"),
    uf: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
):
    sql = """
        SELECT m.id_municipio   AS id_municipio,
               m.nome_municipio AS municipio,
               e.sigla_uf       AS uf,
               COALESCE(p.valor, 0) AS populacao
        FROM municipios m
        JOIN estados e ON e.id_uf = m.id_uf
        LEFT JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        WHERE 1 = 1
    """
    params: list = []
    if q:
        sql += " AND m.nome_municipio LIKE ? "
        params.append(f"%{q}%")
    if uf:
        sql += " AND e.sigla_uf = ? "
        params.append(uf)
    sql += " ORDER BY populacao DESC LIMIT ? "
    params.append(limit)
    return query(sql, tuple(params))


@router.get("/municipios/{id_municipio}", response_model=schemas.MunicipioPopulacao)
def buscar_municipio(id_municipio: int):
    mun = query_one(
        """
        SELECT m.id_municipio   AS id_municipio,
               m.nome_municipio AS municipio,
               e.sigla_uf       AS uf,
               COALESCE(p.valor, 0) AS populacao
        FROM municipios m
        JOIN estados e ON e.id_uf = m.id_uf
        LEFT JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        WHERE m.id_municipio = ?
        """,
        (id_municipio,),
    )
    if not mun:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return mun


@router.post("/municipios", response_model=schemas.MunicipioPopulacao, status_code=201)
def criar_municipio(dados: schemas.MunicipioCreate):
    estado = query_one("SELECT id_uf FROM estados WHERE sigla_uf = ?", (dados.uf,))
    if not estado:
        raise HTTPException(status_code=400, detail=f"UF inválida: {dados.uf}")

    novo_id = query_one(
        "SELECT COALESCE(MAX(id_municipio), 0) + 1 AS novo FROM municipios"
    )["novo"]

    execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, dados.nome, estado["id_uf"]),
    )
    execute(
        """
        INSERT INTO populacao_municipal (id_municipio, ano, valor, indicador, unidade, fonte)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (novo_id, 2025, dados.populacao, "populacao_residente_estimada", "pessoas", "cadastro manual"),
    )
    return buscar_municipio(novo_id)


@router.put("/municipios/{id_municipio}", response_model=schemas.MunicipioPopulacao)
def atualizar_municipio(id_municipio: int, dados: schemas.MunicipioUpdate):
    existente = query_one(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)
    )
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    estado = query_one("SELECT id_uf FROM estados WHERE sigla_uf = ?", (dados.uf,))
    if not estado:
        raise HTTPException(status_code=400, detail=f"UF inválida: {dados.uf}")

    execute(
        "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
        (dados.nome, estado["id_uf"], id_municipio),
    )
    tem_pop = query_one(
        "SELECT 1 AS x FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,)
    )
    if tem_pop:
        execute(
            "UPDATE populacao_municipal SET valor = ? WHERE id_municipio = ?",
            (dados.populacao, id_municipio),
        )
    else:
        execute(
            """
            INSERT INTO populacao_municipal (id_municipio, ano, valor, indicador, unidade, fonte)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (id_municipio, 2025, dados.populacao, "populacao_residente_estimada", "pessoas", "cadastro manual"),
        )
    return buscar_municipio(id_municipio)


@router.delete("/municipios/{id_municipio}", status_code=204)
def remover_municipio(id_municipio: int):
    existente = query_one(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)
    )
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
    execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    execute("DELETE FROM acompanhamento_gestor WHERE id_municipio = ?", (id_municipio,))
    return None


# ###########################################################################
#  PARTE 1C — CADASTRO DO GESTOR (anotações)
# ###########################################################################

@router.get("/acompanhamentos", response_model=List[schemas.Acompanhamento])
def listar_acompanhamentos(id_municipio: Optional[int] = Query(None)):
    sql = """
        SELECT a.id, a.id_municipio, m.nome_municipio AS municipio,
               a.status, a.prioridade, a.observacao, a.responsavel, a.atualizado_em
        FROM acompanhamento_gestor a
        LEFT JOIN municipios m ON m.id_municipio = a.id_municipio
    """
    params: tuple = ()
    if id_municipio is not None:
        sql += " WHERE a.id_municipio = ? "
        params = (id_municipio,)
    sql += " ORDER BY a.atualizado_em DESC "
    return query(sql, params)


@router.post("/acompanhamentos", response_model=schemas.Acompanhamento, status_code=201)
def criar_acompanhamento(dados: schemas.AcompanhamentoCreate):
    mun = query_one(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?", (dados.id_municipio,)
    )
    if not mun:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    execute(
        """
        INSERT INTO acompanhamento_gestor
            (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
        """,
        (dados.id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel),
    )
    novo = query_one("SELECT MAX(id) AS id FROM acompanhamento_gestor")
    return _buscar_acompanhamento(novo["id"])


@router.put("/acompanhamentos/{id_acomp}", response_model=schemas.Acompanhamento)
def atualizar_acompanhamento(id_acomp: int, dados: schemas.AcompanhamentoUpdate):
    if not _buscar_acompanhamento(id_acomp):
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    execute(
        """
        UPDATE acompanhamento_gestor
        SET status = ?, prioridade = ?, observacao = ?, responsavel = ?,
            atualizado_em = datetime('now')
        WHERE id = ?
        """,
        (dados.status, dados.prioridade, dados.observacao, dados.responsavel, id_acomp),
    )
    return _buscar_acompanhamento(id_acomp)


@router.delete("/acompanhamentos/{id_acomp}", status_code=204)
def remover_acompanhamento(id_acomp: int):
    if not _buscar_acompanhamento(id_acomp):
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    execute("DELETE FROM acompanhamento_gestor WHERE id = ?", (id_acomp,))
    return None


def _buscar_acompanhamento(id_acomp: int) -> Optional[dict]:
    return query_one(
        """
        SELECT a.id, a.id_municipio, m.nome_municipio AS municipio,
               a.status, a.prioridade, a.observacao, a.responsavel, a.atualizado_em
        FROM acompanhamento_gestor a
        LEFT JOIN municipios m ON m.id_municipio = a.id_municipio
        WHERE a.id = ?
        """,
        (id_acomp,),
    )