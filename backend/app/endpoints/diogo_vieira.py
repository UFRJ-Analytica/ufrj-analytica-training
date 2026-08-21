from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/diogo-vieira", tags=["diogo_vieira"])

from pydantic import BaseModel

from app.database import query


class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str

class Municipio(BaseModel):
    id_municipio: int
    nome_municipio: str

class NovoMunicipio(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class AtualizacaoMunicipio(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao_atualizada: int | None = None

query("""
    CREATE TABLE IF NOT EXISTS registros (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_municipio INTEGER,
        data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        observacao TEXT,
        FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
    )
""")

@router.get("/status")
def status():
    return {"status": "ok"}

@router.get("/estados", response_model=list[Estado], tags=["dados básicos"])
def listar_estados(
    id_regiao: int | None = Query(default=None),
    limit: int | None = Query(default=None)
):
    sql = """
        SELECT id_uf, sigla_uf, nome_uf
        FROM estados
    """
    params = ()

    if id_regiao is not None:
        sql += " WHERE id_regiao = ?"
        params = (id_regiao,)

    sql += " ORDER BY id_uf"

    if limit is not None:
        sql += " LIMIT ?"
        params = params + (limit,)

    rows = query(sql, params)

    return rows

@router.get("/municipios", response_model=list[Municipio], tags=["dados básicos"])
def listar_municipios(
    id_uf: int | None = Query(default=None),
    limit: int | None = Query(default=None)
):
    sql = """
        SELECT id_municipio, nome_municipio
        FROM municipios
    """
    params = ()

    if id_uf is not None:
        sql += " WHERE id_uf = ?"
        params = (id_uf,)

    sql += " ORDER BY nome_municipio"

    if limit is not None:
        sql += " LIMIT ?"
        params = params + (limit,)

    rows = query(sql, params)

    return rows

@router.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    total_estados = query("""SELECT COUNT(*) AS total_estados FROM estados""")

    total_municipios = query("""SELECT COUNT(*) AS total_municipios FROM municipios""")

    populacao_brasil = query(
        """
            SELECT SUM(valor) AS populacao_total 
            FROM populacao_municipal WHERE ano = (
            SELECT DISTINCT ano 
            FROM populacao_municipal 
            ORDER BY ano DESC LIMIT 1
            )
        """
    )

    ano_referencia = query("""SELECT DISTINCT ano FROM populacao_municipal ORDER BY ano DESC LIMIT 1""")

    return {
        "total_estados": total_estados[0]["total_estados"],
        "total_municipios": total_municipios[0]["total_municipios"],
        "populacao_total": populacao_brasil[0]["populacao_total"],
        "ano": ano_referencia[0]["ano"]
    }

@router.get("/populacao/top-municipios", tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    sql = """
        SELECT m.nome_municipio, p.valor AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        WHERE p.ano = (
            SELECT DISTINCT ano 
            FROM populacao_municipal 
            ORDER BY ano DESC LIMIT 1
        )
        ORDER BY p.valor DESC
        LIMIT ?
    """
    params = (limit,)

    rows = query(sql, params)

    return rows

@router.get("/populacao/por-regiao", tags=["análise"])
def populacao_por_regiao():
    sql = """
        SELECT r.nome_regiao, SUM(p.valor) AS populacao_regional
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        WHERE p.ano = (
            SELECT DISTINCT ano 
            FROM populacao_municipal 
            ORDER BY ano DESC LIMIT 1
        )
        GROUP BY r.nome_regiao
        ORDER BY populacao_regional DESC
    """
    params = ()

    rows = query(sql, params)

    return rows

@router.get("/populacao/por-uf", tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT e.nome_uf, SUM(p.valor) AS populacao_estadual
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        WHERE p.ano = (
            SELECT DISTINCT ano 
            FROM populacao_municipal 
            ORDER BY ano DESC LIMIT 1
        )
    """
    params = ()

    if id_regiao is not None:
        sql += " AND e.id_regiao = ?"
        params = (id_regiao,)

    sql += " GROUP BY e.nome_uf ORDER BY populacao_estadual DESC"
    rows = query(sql, params)

    return rows

@router.get("/populacao/distribuicao", tags=["análise"])
def distribuicao_populacional():
    sql = """
        SELECT valor AS populacao
        FROM populacao_municipal 
        WHERE ano = (
            SELECT DISTINCT ano 
            FROM populacao_municipal 
            ORDER BY ano DESC LIMIT 1
        )
    """
    params = ()

    rows = query(sql, params)

    return rows

@router.get("/populacao/dispersao-uf", tags=["análise"])
def dispersao_por_uf():
    sql = """
        SELECT
            e.nome_uf,
            r.nome_regiao,
            COUNT(m.id_municipio) AS quantidade_municipios,
            AVG(p.valor) AS populacao_media
        FROM populacao_municipal p
        JOIN municipios m
            ON p.id_municipio = m.id_municipio
        JOIN estados e
            ON m.id_uf = e.id_uf
        JOIN regioes r
            ON e.id_regiao = r.id_regiao
        WHERE p.ano = (
            SELECT DISTINCT ano
            FROM populacao_municipal
            ORDER BY ano DESC
            LIMIT 1
        )
        GROUP BY
            e.nome_uf,
            r.nome_regiao
        ORDER BY populacao_media DESC
    """
    params = ()

    rows = query(sql, params)

    return rows

@router.get("/populacao/heatmap-regiao-porte", tags=["análise"])
def heatmap_regiao_porte():
    sql = """
        WITH classificados AS (
            SELECT 
                id_municipio,
                valor,
                NTILE(3) OVER (
                    ORDER BY valor
                ) AS grupo_porte
            FROM populacao_municipal
            WHERE ano = (
                SELECT DISTINCT ano
                FROM populacao_municipal
                ORDER BY ano DESC
                LIMIT 1
            )
        )
        SELECT 
            r.nome_regiao,
            CASE grupo_porte
                WHEN 1 THEN 'Pequeno'
                WHEN 2 THEN 'Médio'
                ELSE 'Grande'
            END AS porte,
            COUNT(m.id_municipio) AS quantidade_municipios
        FROM classificados c
        JOIN municipios m 
            ON c.id_municipio = m.id_municipio
        JOIN estados e 
            ON m.id_uf = e.id_uf
        JOIN regioes r 
            ON e.id_regiao = r.id_regiao
        GROUP BY r.nome_regiao, porte
        ORDER BY quantidade_municipios DESC
    """
    params = ()

    rows = query(sql, params)

    return rows

@router.get("/municipios/{id_municipio}", tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    sql = """
        SELECT m.id_municipio, m.nome_municipio, e.nome_uf, r.nome_regiao, p.valor AS populacao
        FROM municipios m
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        WHERE m.id_municipio = ? AND p.ano = (
            SELECT DISTINCT ano 
            FROM populacao_municipal 
            ORDER BY ano DESC LIMIT 1
        )
    """
    params = (id_municipio,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")
        
    return rows

@router.post("/municipios", tags=["dados básicos"])
def criar_municipio(dados: NovoMunicipio):
    novo_id = query("""
        SELECT COALESCE(MAX(id_municipio), 0) + 1 AS novo_id
        FROM municipios
    """)[0]["novo_id"]

    ano_referencia = query("""
        SELECT MAX(ano) AS ano
        FROM populacao_municipal
    """)[0]["ano"]

    municipios_insertion = query("""
        INSERT INTO municipios (
            id_municipio,
            nome_municipio,
            id_uf
        )
        VALUES (?, ?, ?)
    """, (
        novo_id,
        dados.nome_municipio,
        dados.id_uf
    ))

    populacao_insertion = query("""
        INSERT INTO populacao_municipal (
            id_municipio,
            ano,
            valor
        )
        VALUES (?, ?, ?)
    """, (
        novo_id,
        ano_referencia,
        dados.populacao
    ))

    return municipios_insertion, populacao_insertion

@router.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, dados: AtualizacaoMunicipio):
    sql = """
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
    """
    params = (id_municipio,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    if dados.nome_municipio is not None:
        query("""
            UPDATE municipios
            SET nome_municipio = ?
            WHERE id_municipio = ?
        """, (dados.nome_municipio, id_municipio))

    if dados.id_uf is not None:
        query("""
            UPDATE municipios
            SET id_uf = ?
            WHERE id_municipio = ?
        """, (dados.id_uf, id_municipio))

    if dados.populacao_atualizada is not None:
        query("""
            UPDATE populacao_municipal
            SET valor = ?
            WHERE id_municipio = ? AND ano = (
                SELECT DISTINCT ano
                FROM populacao_municipal
                ORDER BY ano DESC LIMIT 1
            )
        """, (dados.populacao_atualizada, id_municipio))

    infos_atualizadas = query("""
        SELECT m.id_municipio, m.nome_municipio, e.nome_uf, p.valor AS populacao
        FROM municipios m
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        WHERE m.id_municipio = ? AND p.ano = (
            SELECT DISTINCT ano
            FROM populacao_municipal
            ORDER BY ano DESC LIMIT 1
        )
    """, (id_municipio,))

    return infos_atualizadas

@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    sql = """
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
    """
    params = (id_municipio,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    query("""
        DELETE FROM populacao_municipal
        WHERE id_municipio = ?
    """, (id_municipio,))

    query("""
        DELETE FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    return {"message": "Município removido com sucesso"}

@router.post("/municipios/{id_municipio}/registros", tags=["cadastro"])
def criar_registro(id_municipio: int, observacao: str):
    sql = """
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
    """
    params = (id_municipio,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    insertion = query("""
        INSERT INTO registros (id_municipio, data_registro, observacao)
        VALUES (?, ?, ?)
    """, (id_municipio, datetime.now(), observacao))

    return insertion

@router.get("/municipios/{id_municipio}/registros", tags=["cadastro"])
def listar_registros(id_municipio: int):
    sql = """
            SELECT id_municipio
            FROM municipios
            WHERE id_municipio = ?
        """
    params = (id_municipio,)
    
    rows = query(sql, params)
    
    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    sql = """
        SELECT id_registro, id_municipio, data_registro, observacao
        FROM registros
        WHERE id_municipio = ?
        ORDER BY data_registro DESC
    """
    params = (id_municipio,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Nenhum registro encontrado para este município")

    return rows

@router.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, observacao: str | None = None):
    sql = """
        SELECT id_registro
        FROM registros
        WHERE id_registro = ?
    """
    params = (id_registro,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    if observacao is not None:
        query("""
            UPDATE registros
            SET observacao = ?
            WHERE id_registro = ?
        """, (observacao, id_registro))

    infos_atualizadas = query("""
        SELECT id_registro, id_municipio, data_registro, observacao
        FROM registros
        WHERE id_registro = ?
    """, (id_registro,))
    
    return infos_atualizadas

@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    sql = """
        SELECT id_registro
        FROM registros
        WHERE id_registro = ?
    """
    params = (id_registro,)

    rows = query(sql, params)

    if not rows:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    query("""
        DELETE FROM registros
        WHERE id_registro = ?
    """, (id_registro,))

    return {"message": "Registro removido com sucesso"}