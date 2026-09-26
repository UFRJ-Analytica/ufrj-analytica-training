from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.database import get_connection, query

router = APIRouter(prefix="/arthur-pereira", tags=["arthur_pereira"])

def _criar_tabela_cadastro():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cadastro_gestor (
                id_cadastro INTEGER PRIMARY KEY AUTOINCREMENT,
                id_municipio INTEGER NOT NULL,
                status TEXT NOT NULL,
                prioridade TEXT,
                observacao TEXT,
                responsavel TEXT,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
            )
        """)
        conn.commit()
    finally:
        conn.close()


_criar_tabela_cadastro()


class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int = 0


class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None


class RegistroCreate(BaseModel):
    status: str
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None


class RegistroUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None


@router.get("/status")
def status():
    return {"status": "ok"}


@router.get("/regioes")
def listar_regioes():
    """Lista todas as regiões."""
    return query("SELECT * FROM regioes ORDER BY id_regiao")


@router.get("/estados")
def listar_estados(id_regiao: int | None = Query(default=None)):
    """Lista estados com filtro opcional por região."""
    if id_regiao is not None:
        return query("SELECT * FROM estados WHERE id_regiao = ? ORDER BY nome_uf", (id_regiao,))
    return query("SELECT * FROM estados ORDER BY nome_uf")


@router.get("/estatisticas/resumo")
def resumo_estatistico():
    """KPIs principais para o topo do painel."""
    total_municipios = query("SELECT COUNT(*) AS total FROM municipios")[0]["total"]
    total_estados = query("SELECT COUNT(*) AS total FROM estados")[0]["total"]

    pop = query("""
        SELECT SUM(valor) AS populacao_total, MAX(ano) AS ano_referencia
        FROM populacao_municipal
    """)[0]

    mais_populoso = query("""
        SELECT m.nome_municipio, p.valor AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        ORDER BY p.valor DESC
        LIMIT 1
    """)[0]

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": pop["populacao_total"],
        "ano_referencia": pop["ano_referencia"],
        "municipio_mais_populoso": mais_populoso["nome_municipio"],
        "populacao_municipio_mais_populoso": mais_populoso["populacao"],
    }


@router.get("/populacao/top-municipios")
def top_municipios(limit: int = Query(default=10, le=100)):
    """Ranking dos municípios mais populosos."""
    return query("""
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, p.valor AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        ORDER BY p.valor DESC
        LIMIT ?
    """, (limit,))


@router.get("/populacao/por-regiao")
def populacao_por_regiao():
    """População total agregada por região."""
    return query("""
        SELECT r.id_regiao, r.nome_regiao, r.sigla_regiao, SUM(p.valor) AS populacao_total
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        GROUP BY r.id_regiao, r.nome_regiao, r.sigla_regiao
        ORDER BY populacao_total DESC
    """)


@router.get("/populacao/por-uf")
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    """População total por estado, com filtro opcional por região."""
    if id_regiao is not None:
        return query("""
            SELECT e.id_uf, e.nome_uf, e.sigla_uf, SUM(p.valor) AS populacao_total
            FROM populacao_municipal p
            JOIN municipios m ON m.id_municipio = p.id_municipio
            JOIN estados e ON e.id_uf = m.id_uf
            WHERE e.id_regiao = ?
            GROUP BY e.id_uf, e.nome_uf, e.sigla_uf
            ORDER BY populacao_total DESC
        """, (id_regiao,))
    return query("""
        SELECT e.id_uf, e.nome_uf, e.sigla_uf, SUM(p.valor) AS populacao_total
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        GROUP BY e.id_uf, e.nome_uf, e.sigla_uf
        ORDER BY populacao_total DESC
    """)


@router.get("/populacao/distribuicao")
def distribuicao_populacional():
    """População de todos os municípios para histograma."""
    return query("SELECT valor AS populacao FROM populacao_municipal")


@router.get("/populacao/dispersao-uf")
def dispersao_por_uf():
    """Quantidade de municípios e população média por estado, com região para colorir."""
    return query("""
        SELECT e.id_uf, e.nome_uf, e.sigla_uf, r.nome_regiao,
               COUNT(m.id_municipio) AS total_municipios,
               AVG(p.valor) AS populacao_media
        FROM estados e
        JOIN regioes r ON r.id_regiao = e.id_regiao
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        GROUP BY e.id_uf, e.nome_uf, e.sigla_uf, r.nome_regiao
        ORDER BY total_municipios DESC
    """)


@router.get("/populacao/heatmap-regiao-porte")
def heatmap_regiao_porte():
    """Contagem de municípios cruzando região com faixas de porte."""
    return query("""
        SELECT 
            r.nome_regiao,
            CASE 
                WHEN p.valor <= 20000 THEN 'Pequeno (até 20k)'
                WHEN p.valor <= 100000 THEN 'Médio (20k a 100k)'
                ELSE 'Grande (> 100k)'
            END AS porte,
            COUNT(*) AS total_municipios
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao
    """)

@router.get("/municipios")
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    """Lista municípios com filtros de nome, estado e limite."""
    sql = """
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, e.sigla_uf, p.valor AS populacao
        FROM municipios m
        LEFT JOIN estados e ON e.id_uf = m.id_uf
        LEFT JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        WHERE 1=1
    """
    params = []
    if nome:
        sql += " AND m.nome_municipio LIKE ?"
        params.append(f"%{nome}%")
    if id_uf is not None:
        sql += " AND m.id_uf = ?"
        params.append(id_uf)

    sql += " ORDER BY m.nome_municipio LIMIT ?"
    params.append(limit)

    return query(sql, tuple(params))


@router.get("/municipios/{id_municipio}")
def detalhe_municipio(id_municipio: int):
    """Retorna dados completos de um município específico."""
    rows = query("""
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, e.nome_uf, e.sigla_uf,
               p.valor AS populacao, p.ano
        FROM municipios m
        LEFT JOIN estados e ON e.id_uf = m.id_uf
        LEFT JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        WHERE m.id_municipio = ?
    """, (id_municipio,))

    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado.")
    return rows[0]


@router.post("/municipios", status_code=201)
def criar_municipio(dados: MunicipioCreate):
    """Cria um município novo com ID gerado (MAX + 1) e insere sua população inicial."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COALESCE(MAX(id_municipio), 0) + 1 AS novo_id FROM municipios").fetchone()
        novo_id = row["novo_id"]

        conn.execute(
            "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
            (novo_id, dados.nome_municipio, dados.id_uf))
        conn.execute(
            "INSERT INTO populacao_municipal (id_municipio, ano, valor) VALUES (?, 2025, ?)",
            (novo_id, dados.populacao))
        conn.commit()
        return {"id_municipio": novo_id, "mensagem": "Município criado com sucesso!"}
    finally:
        conn.close()


@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    """Atualiza dados do município e/ou sua população."""
    existente = query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    conn = get_connection()
    try:
        if dados.nome_municipio is not None or dados.id_uf is not None:
            conn.execute("""
                UPDATE municipios
                SET nome_municipio = COALESCE(?, nome_municipio),
                    id_uf = COALESCE(?, id_uf)
                WHERE id_municipio = ?
            """, (dados.nome_municipio, dados.id_uf, id_municipio))

        if dados.populacao is not None:
            conn.execute("""
                UPDATE populacao_municipal
                SET valor = ?
                WHERE id_municipio = ?
            """, (dados.populacao, id_municipio))

        conn.commit()
        return {"mensagem": "Município atualizado com sucesso!"}
    finally:
        conn.close()


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    """Remove o município e seus dados associados."""
    existente = query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM cadastro_gestor WHERE id_municipio = ?", (id_municipio,))
        conn.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
        conn.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
        conn.commit()
        return {"mensagem": f"Município {id_municipio} removido com sucesso."}
    finally:
        conn.close()


@router.post("/municipios/{id_municipio}/registros", status_code=201)
def criar_registro(id_municipio: int, dados: RegistroCreate):
    """Cria uma anotação de acompanhamento para o município."""
    existente = query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO cadastro_gestor (id_municipio, status, prioridade, observacao, responsavel)
            VALUES (?, ?, ?, ?, ?)
        """, (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel))
        conn.commit()
        return {"id_cadastro": cursor.lastrowid, "mensagem": "Registro criado com sucesso!"}
    finally:
        conn.close()


@router.get("/municipios/{id_municipio}/registros")
def listar_registros(id_municipio: int):
    """Lista todos os registros de acompanhamento de um município."""
    return query("""
        SELECT * FROM cadastro_gestor
        WHERE id_municipio = ?
        ORDER BY data_criacao DESC
    """, (id_municipio,))


@router.put("/registros/{id_registro}")
def atualizar_registro(id_registro: int, dados: RegistroUpdate):
    """Atualiza uma anotação do gestor existente."""
    existente = query("SELECT id_cadastro FROM cadastro_gestor WHERE id_cadastro = ?", (id_registro,))
    if not existente:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")

    conn = get_connection()
    try:
        conn.execute("""
            UPDATE cadastro_gestor
            SET status = COALESCE(?, status),
                prioridade = COALESCE(?, prioridade),
                observacao = COALESCE(?, observacao),
                responsavel = COALESCE(?, responsavel),
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id_cadastro = ?
        """, (dados.status, dados.prioridade, dados.observacao, dados.responsavel, id_registro))
        conn.commit()
        return {"mensagem": "Registro atualizado com sucesso!"}
    finally:
        conn.close()


@router.delete("/registros/{id_registro}")
def remover_registro(id_registro: int):
    """Remove uma anotação do gestor."""
    existente = query("SELECT id_cadastro FROM cadastro_gestor WHERE id_cadastro = ?", (id_registro,))
    if not existente:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")

    conn = get_connection()
    try:
        conn.execute("DELETE FROM cadastro_gestor WHERE id_cadastro = ?", (id_registro,))
        conn.commit()
        return {"mensagem": f"Registro {id_registro} removido com sucesso."}
    finally:
        conn.close()

