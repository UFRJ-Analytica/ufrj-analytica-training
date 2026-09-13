from fastapi import APIRouter, HTTPException, Query

from app.database import query
from app.schemas import *
import sqlite3
from app.database import DB_PATH

router = APIRouter(
    prefix="/kayky-leandro",
    tags=["Kayky Leandro"]
)


# STATUS


@router.get("/status")
def status():
    return {
        "status": "ok",
        "mensagem": "tudo certo"
    }



# KPIs


@router.get("/estatisticas/resumo")
def resumo_estatistico():
    total_municipios = query("""
    SELECT COUNT(*) AS total FROM municipios
    """)

    total_estados = query("""
    SELECT COUNT(*) AS total FROM estados
    """)

    populacao_total = query("""
    SELECT SUM(valor) AS total FROM populacao_municipal
    """)

    ano_referencia = query("""
    SELECT MAX(ano) AS ano FROM populacao_municipal
    """)

    municipio_mais_populoso = query("""
    SELECT m.nome_municipio, p.valor
        FROM municipios m
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        ORDER BY p.valor DESC
        LIMIT 1
    """)

    return {
        "total_municipios": total_municipios[0]["total"],
        "total_estados": total_estados[0]["total"],
        "populacao_total": populacao_total[0]["total"],
        "ano_referencia": ano_referencia[0]["ano"],
        "municipio_mais_populoso": municipio_mais_populoso[0]["nome_municipio"],
        "populacao_municipio_mais_populoso": municipio_mais_populoso[0]["valor"]
    }

 # ANÁLISES

#TOP MUNICIPIOS
@router.get("/populacao/top-municipios")
def top_municipios(limit: int = Query(default=10, le=100)):

    return query(f"""
        SELECT
            m.nome_municipio,
            p.valor AS populacao

        FROM municipios m

        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio

        ORDER BY p.valor DESC

        LIMIT {limit}
    """)

#POPULAÇÃO POR REGIÃO
@router.get("/populacao/por-regiao")
def populacao_por_regiao():
    return query("""
        SELECT
            r.nome_regiao,
            SUM(p.valor) AS populacao_total
        FROM regioes r
        JOIN estados e
            ON r.id_regiao = e.id_regiao
        JOIN municipios m
            ON e.id_uf = m.id_uf
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        GROUP BY r.nome_regiao
        ORDER BY populacao_total DESC
    """)                

#POPULAÇÃO POR UF
@router.get("/populacao/por-uf")
def populacao_por_uf():

    return query("""
        SELECT
            e.nome_uf,
            SUM(p.valor) AS populacao_total
        FROM estados e
        JOIN municipios m
            ON e.id_uf = m.id_uf
        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio
        GROUP BY e.nome_uf
        ORDER BY populacao_total DESC
    """)

#DISTRIBUIÇÃO DA POPULAÇÃO
@router.get("/populacao/distribuicao")
def distribuicao():

    return query("""
        SELECT valor
        FROM populacao_municipal
    """)

#DISPERSÃO DA POPULAÇÃO POR UF
@router.get("/populacao/dispersao-uf")
def dispersao():

    return query("""
        SELECT
            e.nome_uf,
            r.nome_regiao,
            COUNT(m.id_municipio) AS quantidade_municipios,
            AVG(p.valor) AS populacao_media

        FROM estados e

        JOIN regioes r
            ON e.id_regiao = r.id_regiao

        JOIN municipios m
            ON e.id_uf = m.id_uf

        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio

        GROUP BY
            e.nome_uf,
            r.nome_regiao
    """)

#HEATMAP POR REGIÃO
@router.get("/populacao/heatmap-regiao-porte")
def heatmap():

    return query("""
        SELECT

            r.nome_regiao,

            CASE

                WHEN p.valor < 50000 THEN 'Pequeno'

                WHEN p.valor < 500000 THEN 'Médio'

                ELSE 'Grande'

            END AS porte,

            COUNT(*) AS quantidade

        FROM regioes r

        JOIN estados e
            ON r.id_regiao = e.id_regiao

        JOIN municipios m
            ON e.id_uf = m.id_uf

        JOIN populacao_municipal p
            ON m.id_municipio = p.id_municipio

        GROUP BY
            r.nome_regiao,
            porte

        ORDER BY
            r.nome_regiao
    """)


# MUNICÍPIOS

#LISTA OS MUNICIPIOS
@router.get("/municipios")
def listar_municipios():
    return query("""
        SELECT
            m.id_municipio,
            m.nome_municipio,
            e.nome_uf,
            r.nome_regiao
        FROM municipios m
        JOIN estados e
            ON m.id_uf = e.id_uf
        JOIN regioes r
            ON e.id_regiao = r.id_regiao
    """)

#DETALHA OS MUNICIPIOS
@router.get("/municipios/{id_municipio}")
def detalhe_municipio(id_municipio: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM municipios WHERE id_municipio = ?",
            (id_municipio,)
        )
        municipio = cursor.fetchone()
        if not municipio:
            raise HTTPException(status_code=404, detail="Município não encontrado.")

        return dict(municipio)

    finally:
        conn.close()

#CRIA OS MUNICIPIOS
@router.post("/municipios")
def criar_municipio():
    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO municipios (nome_municipio, id_uf) VALUES (?, ?)",
            ("Novo Município", 1)
        )
        return {"mensagem": "Municipio Criado."}
    finally:
        conn.close()


#ATUALIZA OS MUNICIPIOS
@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int):
    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM municipios WHERE id_municipio = ?",
            (id_municipio,)
        )
        municipio = cursor.fetchone()
        if not municipio:
            raise HTTPException(status_code=404, detail="Município não encontrado.")

        cursor.execute(
            "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
            ("Novo Nome", 1, id_municipio)
        )

        conn.commit()

        return {"mensagem": "Município atualizado."}
    finally:
        conn.close()
    
#DELETA OS MUNICIPIOS
@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM populacao_municipal WHERE id_municipio = ?",
            (id_municipio,)
        )

        cursor.execute(
            "DELETE FROM municipios WHERE id_municipio = ?",
            (id_municipio,)
        )

        conn.commit()

        return {"mensagem": "Município removido."}

    finally:
        conn.close()


# CADASTRO

@router.post("/municipios/{id_municipio}/registros")
def criar_registro(id_municipio: int, status: str, prioridade: str, responsavel: str, observacao: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO registros
        (id_municipio, status, prioridade, responsavel, observacao)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            id_municipio,
            status,
            prioridade,
            responsavel,
            observacao
        ))

        conn.commit()

        return {"mensagem": "Registro criado com sucesso."}
    finally:
        conn.close()


@router.get("/municipios/{id_municipio}/registros")
def listar_registros(id_municipio: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM registros
        WHERE id_municipio = ?
        """, (id_municipio,))

        registros = cursor.fetchall()

        return [dict(registro) for registro in registros]
    finally:
        conn.close()


@router.put("/registros/{id_registro}")
def atualizar_registro(id_registro: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM registros
        WHERE id_registro = ?
        """, (id_registro,))

        registro = cursor.fetchone()
        if not registro:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")

        cursor.execute("""
        UPDATE registros
        SET status = ?, prioridade = ?, responsavel = ?, observacao = ?
        WHERE id_registro = ?
        """,
        (
            "Atualizado",
            "Alta",
            "Novo Responsável",
            "Observação atualizada.",
            id_registro
        ))

        conn.commit()

        return {"mensagem": "Registro atualizado com sucesso."}
    finally:
        conn.close()


@router.delete("/registros/{id_registro}")
def remover_registro(id_registro: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM registros
        WHERE id_registro = ?
        """, (id_registro,))

        registro = cursor.fetchone()
        if not registro:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")

        cursor.execute("""
        DELETE FROM registros
        WHERE id_registro = ?
        """, (id_registro,))

        conn.commit()

        return {"mensagem": "Registro removido com sucesso."}
    finally:
        conn.close()