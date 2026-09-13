from fastapi import APIRouter, Query
from app.database import query, get_connection

router = APIRouter(
    prefix="/julio-menescal",
    tags=["Julio Menescal"]
)

@router.get("/status")
def status():
    return {"status": "ok"}

INDICADOR_POPULACAO = "populacao_residente_estimada"

@router.get("/estatisticas/resumo")
def resumo_estatistico():

    total_municipios = query("""
        SELECT COUNT(*) AS total
        FROM municipios
    """)[0]["total"]

    total_estados = query("""
        SELECT COUNT(*) AS total
        FROM estados
    """)[0]["total"]

    populacao_total = query("""
        SELECT SUM(valor) AS total
        FROM populacao_municipal
        WHERE indicador = ?
    """, (INDICADOR_POPULACAO,))[0]["total"]

    municipio = query("""
        SELECT
            m.nome_municipio,
            p.valor
        FROM municipios m
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        WHERE p.indicador = ?
        ORDER BY p.valor DESC
        LIMIT 1
    """, (INDICADOR_POPULACAO,))[0]

    ano = query("""
        SELECT MAX(ano) AS ano
        FROM populacao_municipal
    """)[0]["ano"]

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "municipio_mais_populoso": municipio["nome_municipio"],
        "populacao_maior_municipio": municipio["valor"],
        "ano_referencia": ano
    }

@router.get("/populacao/top-municipios")
def top_municipios(limit: int = Query(default=10, ge=1, le=100)):
    return query("""
        SELECT
            m.nome_municipio,
            e.sigla_uf,
            p.valor AS populacao
        FROM populacao_municipal p
        JOIN municipios m
            ON p.id_municipio = m.id_municipio
        JOIN estados e
            ON m.id_uf = e.id_uf
        WHERE p.indicador = ?
        ORDER BY p.valor DESC
        LIMIT ?
    """, (INDICADOR_POPULACAO, limit,))

@router.get("/populacao/por-regiao")
def populacao_por_regiao():
    return query("""
        SELECT
            r.nome_regiao,
            r.sigla_regiao,
            SUM(p.valor) AS populacao
        FROM populacao_municipal p
        JOIN municipios m
            ON p.id_municipio = m.id_municipio
        JOIN estados e
            ON m.id_uf = e.id_uf
        JOIN regioes r
            ON e.id_regiao = r.id_regiao
        WHERE p.indicador = ?
        GROUP BY r.id_regiao, r.nome_regiao, r.sigla_regiao
        ORDER BY populacao DESC
    """, (INDICADOR_POPULACAO,))

@router.get("/populacao/por-uf")
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    
    sql = """
        SELECT
            e.nome_uf,
            e.sigla_uf,
            SUM(p.valor) AS populacao
        FROM populacao_municipal p
        JOIN municipios m
            ON p.id_municipio = m.id_municipio
        JOIN estados e
            ON m.id_uf = e.id_uf
        WHERE p.indicador = ?
    """

    params = [INDICADOR_POPULACAO]

    if id_regiao is not None:
        sql += " AND e.id_regiao = ?"
        params.append(id_regiao)

    sql += """
        GROUP BY e.id_uf, e.nome_uf, e.sigla_uf
        ORDER BY populacao DESC
    """

    return query(sql, tuple(params))

@router.get("/populacao/distribuicao")
def distribuicao_populacional():
    return query("""
        SELECT
            valor AS populacao
        FROM populacao_municipal
        WHERE indicador = ?
        ORDER BY valor
    """, (INDICADOR_POPULACAO,))

@router.get("/populacao/dispersao-uf")
def dispersao_por_uf():
    return query("""
        SELECT
            e.nome_uf,
            e.sigla_uf,
            r.sigla_regiao,
            COUNT(m.id_municipio) AS quantidade_municipios,
            AVG(p.valor) AS populacao_media
        FROM estados e
        JOIN municipios m
            ON e.id_uf = m.id_uf
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        JOIN regioes r
            ON e.id_regiao = r.id_regiao
        WHERE p.indicador = ?
        GROUP BY
            e.id_uf,
            e.nome_uf,
            e.sigla_uf,
            r.sigla_regiao
        ORDER BY populacao_media DESC
    """, (INDICADOR_POPULACAO,))


@router.get("/populacao/heatmap")
def heatmap_populacao():
    return query("""
        SELECT
            r.nome_regiao,
            CASE
                WHEN p.valor <= 20000 THEN 'Pequeno'
                WHEN p.valor <= 100000 THEN 'Médio'
                ELSE 'Grande'
            END AS porte,
            COUNT(*) AS quantidade_municipios
        FROM populacao_municipal p
        JOIN municipios m
            ON p.id_municipio = m.id_municipio
        JOIN estados e
            ON m.id_uf = e.id_uf
        JOIN regioes r
            ON e.id_regiao = r.id_regiao
        WHERE p.indicador = ?
        GROUP BY
            r.nome_regiao,
            porte
        ORDER BY
            r.nome_regiao,
            porte
    """, (INDICADOR_POPULACAO,))

# CRUD

def execute(sql: str, params: tuple = ()) -> int:
    """
    Executa INSERT, UPDATE e DELETE.
    Retorna o número de linhas afetadas.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

from pydantic import BaseModel


class Regiao(BaseModel):
    id_regiao: int
    sigla_regiao: str
    nome_regiao: str


class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioUpdate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioResponse(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int

@router.get("/municipios", response_model=list[MunicipioResponse])
def listar_municipios():
    return query("""
        SELECT
            m.id_municipio,
            m.nome_municipio,
            m.id_uf,
            p.valor AS populacao
        FROM municipios m
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        WHERE p.indicador = ?
        ORDER BY m.nome_municipio
    """, (INDICADOR_POPULACAO,))

from fastapi import HTTPException

@router.get("/municipios/{id_municipio}", response_model=MunicipioResponse)
def buscar_municipio(id_municipio: int):
    resultado = query("""
        SELECT
            m.id_municipio,
            m.nome_municipio,
            m.id_uf,
            p.valor AS populacao
        FROM municipios m
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        WHERE
            m.id_municipio = ?
            AND p.indicador = ?
    """, (id_municipio, INDICADOR_POPULACAO))

    if not resultado:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    return resultado[0]

@router.post("/municipios", response_model=MunicipioResponse)
def criar_municipio(municipio: MunicipioCreate):
    # Gera um novo id_municipio
    novo_id = query("""
        SELECT COALESCE(MAX(id_municipio), 0) + 1 AS novo_id
        FROM municipios
    """)[0]["novo_id"]

    # Insere na tabela municipios
    execute("""
        INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
        VALUES (?, ?, ?)
    """, (
        novo_id,
        municipio.nome_municipio,
        municipio.id_uf
    ))

    # Insere a população
    execute("""
        INSERT INTO populacao_municipal (
            id_municipio,
            ano,
            indicador,
            valor,
            unidade,
            fonte
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        novo_id,
        2024,
        INDICADOR_POPULACAO,
        municipio.populacao,
        "habitantes",
        "Cadastro"
    ))

    return {
        "id_municipio": novo_id,
        "nome_municipio": municipio.nome_municipio,
        "id_uf": municipio.id_uf,
        "populacao": municipio.populacao
    }

@router.put("/municipios/{id_municipio}", response_model=MunicipioResponse)
def atualizar_municipio(id_municipio: int, municipio: MunicipioUpdate):

    existe = query("""
        SELECT 1
        FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    if not existe:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    execute("""
        UPDATE municipios
        SET
            nome_municipio = ?,
            id_uf = ?
        WHERE id_municipio = ?
    """, (
        municipio.nome_municipio,
        municipio.id_uf,
        id_municipio
    ))

    execute("""
        UPDATE populacao_municipal
        SET valor = ?
        WHERE
            id_municipio = ?
            AND indicador = ?
    """, (
        municipio.populacao,
        id_municipio,
        INDICADOR_POPULACAO
    ))

    return {
        "id_municipio": id_municipio,
        "nome_municipio": municipio.nome_municipio,
        "id_uf": municipio.id_uf,
        "populacao": municipio.populacao
    }

@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):

    existe = query("""
        SELECT 1
        FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    if not existe:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    execute("""
        DELETE FROM populacao_municipal
        WHERE id_municipio = ?
    """, (id_municipio,))

    execute("""
        DELETE FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    return {
        "mensagem": "Município removido com sucesso."
    }

# MODELOS PYDANTIC

class CadastroCreate(BaseModel):
    id_municipio: int
    status: str
    prioridade: str
    responsavel: str
    observacao: str | None = None


class CadastroUpdate(BaseModel):
    status: str
    prioridade: str
    responsavel: str
    observacao: str | None = None


class CadastroResponse(BaseModel):
    id: int
    id_municipio: int
    status: str
    prioridade: str
    responsavel: str
    observacao: str | None = None

@router.get("/cadastros", response_model=list[CadastroResponse])
def listar_cadastros():
    return query("""
        SELECT
            id,
            id_municipio,
            status,
            prioridade,
            responsavel,
            observacao
        FROM cadastro
        ORDER BY id
    """)

@router.get("/cadastros/{id}", response_model=CadastroResponse)
def buscar_cadastro(id: int):
    resultado = query("""
        SELECT
            id,
            id_municipio,
            status,
            prioridade,
            responsavel,
            observacao
        FROM cadastro
        WHERE id = ?
    """, (id,))

    if not resultado:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado."
        )

    return resultado[0]

@router.post("/cadastros", response_model=CadastroResponse)
def criar_cadastro(cadastro: CadastroCreate):

    municipio = query("""
        SELECT 1
        FROM municipios
        WHERE id_municipio = ?
    """, (cadastro.id_municipio,))

    if not municipio:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    novo_id = query("""
        SELECT COALESCE(MAX(id), 0) + 1 AS novo_id
        FROM cadastro
    """)[0]["novo_id"]

    execute("""
        INSERT INTO cadastro (
            id,
            id_municipio,
            status,
            prioridade,
            responsavel,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        novo_id,
        cadastro.id_municipio,
        cadastro.status,
        cadastro.prioridade,
        cadastro.responsavel,
        cadastro.observacao
    ))

    return {
        "id": novo_id,
        "id_municipio": cadastro.id_municipio,
        "status": cadastro.status,
        "prioridade": cadastro.prioridade,
        "responsavel": cadastro.responsavel,
        "observacao": cadastro.observacao
    }

@router.put("/cadastros/{id}", response_model=CadastroResponse)
def atualizar_cadastro(id: int, cadastro: CadastroUpdate):

    existe = query("""
        SELECT id_municipio
        FROM cadastro
        WHERE id = ?
    """, (id,))

    if not existe:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado."
        )

    id_municipio = existe[0]["id_municipio"]

    execute("""
        UPDATE cadastro
        SET
            status = ?,
            prioridade = ?,
            responsavel = ?,
            observacao = ?
        WHERE id = ?
    """, (
        cadastro.status,
        cadastro.prioridade,
        cadastro.responsavel,
        cadastro.observacao,
        id
    ))

    return {
        "id": id,
        "id_municipio": id_municipio,
        "status": cadastro.status,
        "prioridade": cadastro.prioridade,
        "responsavel": cadastro.responsavel,
        "observacao": cadastro.observacao
    }

@router.delete("/cadastros/{id}")
def remover_cadastro(id: int):

    existe = query("""
        SELECT 1
        FROM cadastro
        WHERE id = ?
    """, (id,))

    if not existe:
        raise HTTPException(
            status_code=404,
            detail="Cadastro não encontrado."
        )

    execute("""
        DELETE FROM cadastro
        WHERE id = ?
    """, (id,))

    return {
        "mensagem": "Cadastro removido com sucesso."
    }