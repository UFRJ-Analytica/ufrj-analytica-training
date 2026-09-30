from fastapi import APIRouter, Query, HTTPException
from app.database import get_connection, query
from pydantic import BaseModel

router = APIRouter(tags=["dados básicos"])

INDICADOR_POPULACAO = "populacao_residente_estimada"
ANO_REFERENCIA = 2025

TABELA_REGISTROS = "acompanhamento_municipio"


class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None


class RegistroCreate(BaseModel):
    status: str = "monitorando"
    prioridade: str = "media"
    observacao: str | None = None
    responsavel: str | None = None


class RegistroUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None


def _criar_tabela_registros():
    conn = get_connection()
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABELA_REGISTROS} (
            id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
            id_municipio INTEGER NOT NULL REFERENCES municipios(id_municipio),
            status TEXT,
            prioridade TEXT,
            observacao TEXT,
            responsavel TEXT,
            criado_em TEXT DEFAULT (datetime('now')),
            atualizado_em TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

_criar_tabela_registros()


@router.get("/estados")
def listar_estados(id_regiao: int | None = Query(default=None)):
    if id_regiao is None:
        return query("SELECT * FROM estados")
    return query("SELECT * FROM estados WHERE id_regiao = ?", (id_regiao,))


@router.get("/municipios")
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    sql = "SELECT * FROM municipios WHERE 1=1"
    params = []
    if nome is not None:
        sql += " AND nome_municipio = ?"
        params.append(nome)
    if id_uf is not None:
        sql += " AND id_uf = ?"
        params.append(id_uf)
    sql += " LIMIT ?"
    params.append(limit)
    return query(sql, params)


@router.get("/municipios/{id_municipio}")
def detalhe_municipio(id_municipio: int):
    rows = query("""
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, f.valor AS populacao
        FROM municipios m
        LEFT JOIN fato_indicador_municipal f
            ON f.id_municipio = m.id_municipio
            AND f.indicador = ? AND f.ano = ?
        WHERE m.id_municipio = ?
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA, id_municipio))
    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado.")
    return rows[0]


@router.post("/municipios")
def criar_municipio(municipio: MunicipioCreate):
    conn = get_connection()
    cur = conn.cursor()

    resultado = query("SELECT MAX(id_municipio) AS maior_id FROM municipios")
    novo_id = (resultado[0]["maior_id"] or 0) + 1

    cur.execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, municipio.nome_municipio, municipio.id_uf),
    )
    cur.execute(
        "INSERT INTO fato_indicador_municipal (id_municipio, valor, indicador, ano) VALUES (?, ?, ?, ?)",
        (novo_id, municipio.populacao, INDICADOR_POPULACAO, ANO_REFERENCIA),
    )
    conn.commit()
    conn.close()

    return {"id_municipio": novo_id, **municipio.model_dump()}


@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    conn = get_connection()
    cur = conn.cursor()

    existe = query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    campos, valores = [], []
    if dados.nome_municipio is not None:
        campos.append("nome_municipio = ?")
        valores.append(dados.nome_municipio)
    if dados.id_uf is not None:
        campos.append("id_uf = ?")
        valores.append(dados.id_uf)

    if campos:
        sql = "UPDATE municipios SET " + ", ".join(campos) + " WHERE id_municipio = ?"
        valores.append(id_municipio)
        cur.execute(sql, valores)

    if dados.populacao is not None:
        cur.execute("""
            INSERT INTO fato_indicador_municipal (id_municipio, valor, indicador, ano)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id_municipio, ano, indicador) DO UPDATE SET valor = excluded.valor
        """, (id_municipio, dados.populacao, INDICADOR_POPULACAO, ANO_REFERENCIA))

    conn.commit()
    conn.close()
    return detalhe_municipio(id_municipio)


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    conn = get_connection()
    cur = conn.cursor()

    existe = query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    cur.execute("DELETE FROM fato_indicador_municipal WHERE id_municipio = ?", (id_municipio,))
    cur.execute(f"DELETE FROM {TABELA_REGISTROS} WHERE id_municipio = ?", (id_municipio,))
    cur.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    conn.commit()
    conn.close()
    return {"mensagem": "Município removido com sucesso."}


@router.get("/estatisticas/resumo")
def resumo_estatistico():
    total_municipios = query("SELECT COUNT(*) AS total FROM municipios")[0]["total"]
    total_estados = query("SELECT COUNT(*) AS total FROM estados")[0]["total"]

    populacao_total = query(
        "SELECT SUM(valor) AS total FROM fato_indicador_municipal WHERE indicador = ? AND ano = ?",
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )[0]["total"]

    mais_populoso = query("""
        SELECT m.nome_municipio, f.valor
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        WHERE f.indicador = ? AND f.ano = ?
        ORDER BY f.valor DESC
        LIMIT 1
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA))[0]

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": ANO_REFERENCIA,
        "municipio_mais_populoso": mais_populoso["nome_municipio"],
        "populacao_municipio_mais_populoso": mais_populoso["valor"],
    }


@router.get("/populacao/top-municipios")
def top_municipios(limit: int = Query(default=10, le=100)):
    return query("""
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, f.valor AS populacao
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        WHERE f.indicador = ? AND f.ano = ?
        ORDER BY f.valor DESC
        LIMIT ?
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA, limit))


@router.get("/populacao/por-regiao")
def populacao_por_regiao():
    return query("""
        SELECT r.nome_regiao, SUM(f.valor) AS populacao
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        WHERE f.indicador = ? AND f.ano = ?
        GROUP BY r.nome_regiao
        ORDER BY populacao DESC
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA))


@router.get("/populacao/por-uf")
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT e.id_uf, e.nome_uf, e.sigla_uf, SUM(f.valor) AS populacao
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        WHERE f.indicador = ? AND f.ano = ?
    """
    params = [INDICADOR_POPULACAO, ANO_REFERENCIA]
    if id_regiao is not None:
        sql += " AND e.id_regiao = ?"
        params.append(id_regiao)
    sql += " GROUP BY e.id_uf, e.nome_uf, e.sigla_uf ORDER BY populacao DESC"
    return query(sql, params)


@router.get("/populacao/distribuicao")
def distribuicao_populacional():
    return query("""
        SELECT m.id_municipio, m.nome_municipio, f.valor AS populacao
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        WHERE f.indicador = ? AND f.ano = ?
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA))


@router.get("/populacao/dispersao-uf")
def dispersao_por_uf():
    return query("""
        SELECT e.nome_uf, e.sigla_uf, r.nome_regiao,
               COUNT(m.id_municipio) AS qtd_municipios,
               AVG(f.valor) AS populacao_media
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        WHERE f.indicador = ? AND f.ano = ?
        GROUP BY e.nome_uf, e.sigla_uf, r.nome_regiao
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA))


@router.get("/populacao/heatmap-regiao-porte")
def heatmap_regiao_porte():
    rows = query("""
        SELECT r.nome_regiao, f.valor
        FROM fato_indicador_municipal f
        JOIN municipios m ON f.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        WHERE f.indicador = ? AND f.ano = ?
    """, (INDICADOR_POPULACAO, ANO_REFERENCIA))

    def classificar(pop):
        if pop < 20000:
            return "pequeno"
        elif pop < 100000:
            return "médio"
        return "grande"

    contagem = {}
    for row in rows:
        chave = (row["nome_regiao"], classificar(row["valor"]))
        contagem[chave] = contagem.get(chave, 0) + 1

    return [
        {"regiao": regiao, "porte": porte, "quantidade": qtd}
        for (regiao, porte), qtd in contagem.items()
    ]


@router.post("/municipios/{id_municipio}/registros")
def criar_registro(id_municipio: int, dados: RegistroCreate):
    if not query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)):
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABELA_REGISTROS} (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
    """, (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel))
    novo_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "id_registro": novo_id,
        "id_municipio": id_municipio,
        "status": dados.status,
        "prioridade": dados.prioridade,
        "observacao": dados.observacao,
        "responsavel": dados.responsavel,
    }


@router.get("/municipios/{id_municipio}/registros")
def listar_registros(id_municipio: int):
    return query(
        f"SELECT * FROM {TABELA_REGISTROS} WHERE id_municipio = ? ORDER BY id_registro DESC",
        (id_municipio,),
    )


@router.put("/registros/{id_registro}")
def atualizar_registro(id_registro: int, dados: RegistroUpdate):
    if not query(f"SELECT id_registro FROM {TABELA_REGISTROS} WHERE id_registro = ?", (id_registro,)):
        raise HTTPException(status_code=404, detail="Registro não encontrado.")

    campos, valores = [], []
    if dados.status is not None:
        campos.append("status = ?")
        valores.append(dados.status)
    if dados.prioridade is not None:
        campos.append("prioridade = ?")
        valores.append(dados.prioridade)
    if dados.observacao is not None:
        campos.append("observacao = ?")
        valores.append(dados.observacao)
    if dados.responsavel is not None:
        campos.append("responsavel = ?")
        valores.append(dados.responsavel)
    campos.append("atualizado_em = datetime('now')")

    conn = get_connection()
    cur = conn.cursor()
    sql = f"UPDATE {TABELA_REGISTROS} SET " + ", ".join(campos) + " WHERE id_registro = ?"
    valores.append(id_registro)
    cur.execute(sql, valores)
    conn.commit()
    conn.close()

    return query(f"SELECT * FROM {TABELA_REGISTROS} WHERE id_registro = ?", (id_registro,))[0]


@router.delete("/registros/{id_registro}")
def remover_registro(id_registro: int):
    if not query(f"SELECT id_registro FROM {TABELA_REGISTROS} WHERE id_registro = ?", (id_registro,)):
        raise HTTPException(status_code=404, detail="Registro não encontrado.")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {TABELA_REGISTROS} WHERE id_registro = ?", (id_registro,))
    conn.commit()
    conn.close()
    return {"mensagem": "Registro removido com sucesso."}