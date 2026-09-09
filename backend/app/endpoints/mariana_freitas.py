import sqlite3
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel


DB_PATH = (
    Path(__file__).resolve().parents[3]
    / "entregaveis"
    / "banco_de_dados"
    / "mariana_freitas_trainee"
    / "database.db"
)


def get_connection():
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

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None


class RegistroCreate(BaseModel):
    status: str
    prioridade: str
    observacao: str | None = None
    responsavel: str | None = None


class RegistroUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None


router = APIRouter(
    prefix="/mariana-freitas",
    tags=["Mariana Freitas"]
)


@router.get("/status")
def status():
    return {"status": "ok"}


@router.get("/estatisticas/resumo")
def resumo():

    municipios = query("""
        SELECT COUNT(*) AS total
        FROM municipios
    """)

    estados = query("""
        SELECT COUNT(*) AS total
        FROM estados
    """)

    populacao = query("""
    SELECT SUM(valor) AS total
    FROM populacao_municipal
    WHERE ano = (
        SELECT MAX(ano)
        FROM populacao_municipal
    )
""")

    ano = query("""
        SELECT MAX(ano) AS ano
        FROM populacao_municipal
    """)

    mais_populoso = query("""
        SELECT
            m.nome_municipio,
            p.valor AS populacao
        FROM municipios m
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        ORDER BY p.valor DESC
        LIMIT 1
    """)

    return {
        "total_municipios": municipios[0]["total"],
        "total_estados": estados[0]["total"],
        "populacao_total": populacao[0]["total"],
        "ano_referencia": ano[0]["ano"],
        "municipio_mais_populoso": mais_populoso[0]["nome_municipio"]
    }


@router.get("/populacao/top-municipios")
def top_municipios(limit: int = Query(default=10, le=100)):

    resultado = query("""
    SELECT
        m.nome_municipio,
        e.sigla_uf,
        p.valor AS populacao
    FROM municipios m
    JOIN estados e
        ON m.id_uf = e.id_uf
    JOIN populacao_municipal p
        ON m.id_municipio = p.id_municipio
    WHERE p.indicador = 'populacao_residente_estimada'
    ORDER BY p.valor DESC
    LIMIT ?
""", (limit,))

    return resultado


@router.get("/populacao/por-regiao")
def populacao_por_regiao():

    resultado = query("""
    SELECT
        r.sigla_regiao,
        r.nome_regiao,
        SUM(p.valor) AS populacao_total
    FROM regioes r
    JOIN estados e
        ON e.id_regiao = r.id_regiao
    JOIN municipios m
        ON m.id_uf = e.id_uf
    JOIN populacao_municipal p
        ON p.id_municipio = m.id_municipio
    WHERE p.indicador = 'populacao_residente_estimada'
    GROUP BY r.id_regiao
    ORDER BY populacao_total DESC
""")

    return resultado


@router.get("/populacao/por-uf")
def populacao_por_uf(
    id_regiao: int | None = Query(default=None)
):

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
    """

    params = ()

    if id_regiao is not None:
        sql += " WHERE e.id_regiao = ?"
        params = (id_regiao,)

    sql += """
        GROUP BY
            e.nome_uf,
            e.sigla_uf

        ORDER BY populacao DESC
    """

    return query(sql, params)


@router.get("/populacao/distribuicao")
def distribuicao_populacional():

    resultado = query("""
        SELECT
            m.nome_municipio,
            p.valor AS populacao

        FROM municipios m

        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio

        ORDER BY populacao DESC
    """)

    return resultado


@router.get("/populacao/dispersao-uf")
def dispersao_por_uf():

    resultado = query("""
        SELECT
            e.nome_uf,
            e.sigla_uf,
            COUNT(m.id_municipio) AS quantidade_municipios,
            ROUND(AVG(p.valor), 2) AS populacao_media

        FROM estados e

        JOIN municipios m
            ON e.id_uf = m.id_uf

        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio

        GROUP BY
            e.id_uf,
            e.nome_uf,
            e.sigla_uf

        ORDER BY quantidade_municipios DESC
    """)

    return resultado


@router.get("/populacao/heatmap-regiao-porte")
def heatmap_regiao_porte():

    resultado = query("""
        SELECT
            r.nome_regiao,

            CASE
                WHEN p.valor <= 50000 THEN 'Pequeno'
                WHEN p.valor <= 200000 THEN 'Médio'
                ELSE 'Grande'
            END AS porte,

            COUNT(*) AS quantidade

        FROM populacao_municipal p

        JOIN municipios m
            ON p.id_municipio = m.id_municipio

        JOIN estados e
            ON m.id_uf = e.id_uf

        JOIN regioes r
            ON e.id_regiao = r.id_regiao

        GROUP BY
            r.nome_regiao,
            porte

        ORDER BY
            r.nome_regiao,
            porte
    """)

    return resultado


@router.get("/municipios")
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500)
):

    sql = """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            e.nome_uf,
            e.sigla_uf

        FROM municipios m

        JOIN estados e
            ON m.id_uf = e.id_uf

        WHERE 1=1
    """

    params = []

    if nome is not None:
        sql += " AND m.nome_municipio LIKE ?"
        params.append(f"%{nome}%")

    if id_uf is not None:
        sql += " AND m.id_uf = ?"
        params.append(id_uf)

    sql += """
        ORDER BY m.nome_municipio
        LIMIT ?
    """

    params.append(limit)

    return query(sql, tuple(params))


@router.get("/municipios/{id_municipio}")
def buscar_municipio(id_municipio: int):

    resultado = query("""
        SELECT
            m.id_municipio,
            m.nome_municipio,
            e.nome_uf,
            e.sigla_uf,
            r.nome_regiao,
            p.ano,
            p.valor AS populacao,
            p.unidade,
            p.fonte

        FROM municipios m

        JOIN estados e
            ON m.id_uf = e.id_uf

        JOIN regioes r
            ON e.id_regiao = r.id_regiao

        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio

        WHERE m.id_municipio = ?
    """, (id_municipio,))

    if not resultado:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    return resultado[0]


@router.post("/municipios")
def criar_municipio(municipio: MunicipioCreate):

    ultimo_id = query("""
        SELECT MAX(id_municipio) AS max_id
        FROM municipios
    """)

    novo_id = ultimo_id[0]["max_id"] + 1

    execute("""
        INSERT INTO municipios (
            id_municipio,
            nome_municipio,
            id_uf
        )
        VALUES (?, ?, ?)
    """, (
        novo_id,
        municipio.nome_municipio,
        municipio.id_uf
    ))

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
        2025,
        "populacao_residente_estimada",
        municipio.populacao,
        "pessoas",
        "Cadastro Manual"
    ))

    return {
        "mensagem": "Município criado com sucesso.",
        "id_municipio": novo_id
    }


@router.put("/municipios/{id_municipio}")
def atualizar_municipio(
    id_municipio: int,
    municipio: MunicipioUpdate
):

    existente = query("""
        SELECT
            id_municipio,
            nome_municipio,
            id_uf
        FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    if not existente:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    if municipio.nome_municipio is not None:
        execute("""
            UPDATE municipios
            SET nome_municipio = ?
            WHERE id_municipio = ?
        """, (
            municipio.nome_municipio,
            id_municipio
        ))

    if municipio.id_uf is not None:
        execute("""
            UPDATE municipios
            SET id_uf = ?
            WHERE id_municipio = ?
        """, (
            municipio.id_uf,
            id_municipio
        ))

    if municipio.populacao is not None:
        execute("""
            UPDATE populacao_municipal
            SET valor = ?
            WHERE id_municipio = ?
              AND indicador = 'populacao_residente_estimada'
        """, (
            municipio.populacao,
            id_municipio
        ))

    return {
        "mensagem": "Município atualizado com sucesso.",
        "id_municipio": id_municipio
    }


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):

    existente = query("""
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    if not existente:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    execute("""
        DELETE FROM registros_municipais
        WHERE id_municipio = ?
    """, (id_municipio,))

    execute("""
        DELETE FROM populacao_municipal
        WHERE id_municipio = ?
    """, (id_municipio,))

    execute("""
        DELETE FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    return {
        "mensagem": "Município removido com sucesso.",
        "id_municipio": id_municipio
    }


@router.post("/municipios/{id_municipio}/registros")
def criar_registro(
    id_municipio: int,
    registro: RegistroCreate
):

    municipio = query("""
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    if not municipio:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    execute("""
        INSERT INTO registros_municipais (
            id_municipio,
            status,
            prioridade,
            observacao,
            responsavel
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        id_municipio,
        registro.status,
        registro.prioridade,
        registro.observacao,
        registro.responsavel
    ))

    resultado = query("""
        SELECT MAX(id_registro) AS id_registro
        FROM registros_municipais
        WHERE id_municipio = ?
    """, (id_municipio,))

    return {
        "mensagem": "Registro criado com sucesso.",
        "id_registro": resultado[0]["id_registro"],
        "id_municipio": id_municipio
    }

@router.get("/municipios/{id_municipio}/registros")
def listar_registros(id_municipio: int):

    municipio = query("""
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
    """, (id_municipio,))

    if not municipio:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado."
        )

    registros = query("""
        SELECT
            id_registro,
            id_municipio,
            status,
            prioridade,
            observacao,
            responsavel
        FROM registros_municipais
        WHERE id_municipio = ?
        ORDER BY id_registro
    """, (id_municipio,))

    return registros


@router.put("/registros/{id_registro}")
def atualizar_registro(
    id_registro: int,
    registro: RegistroUpdate
):

    existente = query("""
        SELECT id_registro
        FROM registros_municipais
        WHERE id_registro = ?
    """, (id_registro,))

    if not existente:
        raise HTTPException(
            status_code=404,
            detail="Registro não encontrado."
        )

    if registro.status is not None:
        execute("""
            UPDATE registros_municipais
            SET status = ?
            WHERE id_registro = ?
        """, (registro.status, id_registro))

    if registro.prioridade is not None:
        execute("""
            UPDATE registros_municipais
            SET prioridade = ?
            WHERE id_registro = ?
        """, (registro.prioridade, id_registro))

    if registro.observacao is not None:
        execute("""
            UPDATE registros_municipais
            SET observacao = ?
            WHERE id_registro = ?
        """, (registro.observacao, id_registro))

    if registro.responsavel is not None:
        execute("""
            UPDATE registros_municipais
            SET responsavel = ?
            WHERE id_registro = ?
        """, (registro.responsavel, id_registro))

    return {
        "mensagem": "Registro atualizado com sucesso.",
        "id_registro": id_registro
    }


@router.delete("/registros/{id_registro}")
def remover_registro(id_registro: int):

    existente = query("""
        SELECT id_registro
        FROM registros_municipais
        WHERE id_registro = ?
    """, (id_registro,))

    if not existente:
        raise HTTPException(
            status_code=404,
            detail="Registro não encontrado."
        )

    execute("""
        DELETE FROM registros_municipais
        WHERE id_registro = ?
    """, (id_registro,))

    return {
        "mensagem": "Registro removido com sucesso.",
        "id_registro": id_registro
    }
