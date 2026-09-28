from fastapi import APIRouter
from app.database import query

router = APIRouter(prefix="/eduardo-borges", tags=["eduardo_borges"])

# Endpoint de teste de status
@router.get("/status")
def status():
    return {"status": "ok", "desenvolvedor": "Eduardo Borges"}

# 1. NÚMEROS RESUMO (KPIs)
@router.get("/kpis")
def get_kpis():
    """
    Retorna: total de municípios, total de estados, população total do Brasil,
    ano de referência e o município mais populoso.
    """
    tot_mun = query("SELECT COUNT(*) as total FROM municipios")[0]["total"]
    tot_uf = query("SELECT COUNT(*) as total FROM estados")[0]["total"]
    tot_pop = query("SELECT SUM(valor) as total FROM populacao_municipal")[0]["total"]
    
    top_mun = query("""
        SELECT m.nome_municipio, p.valor as populacao
        FROM municipios m 
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
        ORDER BY p.valor DESC 
        LIMIT 1
    """)
    
    nome_top = top_mun[0]["nome_municipio"] if top_mun else "N/A"
    pop_top = top_mun[0]["populacao"] if top_mun else 0
    
    return {
        "total_municipios": tot_mun,
        "total_estados": tot_uf,
        "populacao_total_brasil": tot_pop,
        "ano_referencia": 2025,
        "municipio_mais_populoso": nome_top,
        "populacao_mais_populoso": pop_top
    }

from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel
from app.database import get_connection

# ==========================================
# SCHEMAS PYDANTIC (Estrutura das requisições)
# ==========================================

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class MunicipioUpdate(BaseModel):
    nome_municipio: Optional[str] = None
    id_uf: Optional[int] = None
    populacao: Optional[int] = None

class ObservacaoCreate(BaseModel):
    id_municipio: int
    status: str          # ex: "Em Acompanhamento", "Concluído"
    prioridade: str      # ex: "Baixa", "Média", "Alta"
    observacao: str
    responsavel: str

class ObservacaoUpdate(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


# ==========================================
# MUNICÍPIO (DADOS BÁSICOS) - POST, PUT, DELETE
# ==========================================

@router.post("/municipios", status_code=201)
def criar_municipio(mun: MunicipioCreate):
    """Cria um município novo gerando id_municipio automático (maior ID + 1)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        max_id = cursor.execute("SELECT MAX(id_municipio) FROM municipios").fetchone()[0] or 0
        novo_id = max_id + 1
        
        cursor.execute("INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
                       (novo_id, mun.nome_municipio, mun.id_uf))
        cursor.execute("INSERT INTO populacao_municipal (id_municipio, valor, ano) VALUES (?, ?, 2025)",
                       (novo_id, mun.populacao))
        conn.commit()
        return {"mensagem": "Município criado com sucesso!", "id_municipio": novo_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int, mun: MunicipioUpdate):
    """Atualiza dados de um município existente."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        existe = cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone()
        if not existe:
            raise HTTPException(status_code=404, detail="Município não encontrado.")

        if mun.nome_municipio or mun.id_uf:
            cursor.execute("""
                UPDATE municipios 
                SET nome_municipio = COALESCE(?, nome_municipio), id_uf = COALESCE(?, id_uf)
                WHERE id_municipio = ?
            """, (mun.nome_municipio, mun.id_uf, id_municipio))
            
        if mun.populacao is not None:
            cursor.execute("""
                UPDATE populacao_municipal 
                SET valor = ? 
                WHERE id_municipio = ?
            """, (mun.populacao, id_municipio))
            
        conn.commit()
        return {"mensagem": "Município atualizado com sucesso!"}
    finally:
        conn.close()

@router.delete("/municipios/{id_municipio}")
def deletar_municipio(id_municipio: int):
    """Remove um município e seus dados vinculados."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        existe = cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone()
        if not existe:
            raise HTTPException(status_code=404, detail="Município não encontrado.")

        cursor.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
        cursor.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
        cursor.execute("DELETE FROM observacoes_gestor WHERE id_municipio = ?", (id_municipio,))
        conn.commit()
        return {"mensagem": "Município removido com sucesso!"}
    finally:
        conn.close()


# ==========================================
# CADASTRO DE ANOTAÇÕES DO GESTOR - CRUD
# ==========================================

@router.get("/observacoes")
def listar_observacoes(id_municipio: Optional[int] = None):
    """Lista anotações dos gestores (com filtro opcional por município)."""
    sql = """
        SELECT o.*, m.nome_municipio 
        FROM observacoes_gestor o
        JOIN municipios m ON o.id_municipio = m.id_municipio
    """
    params = ()
    if id_municipio:
        sql += " WHERE o.id_municipio = ?"
        params = (id_municipio,)
    return query(sql, params)

@router.post("/observacoes", status_code=201)
def criar_observacao(obs: ObservacaoCreate):
    """Cria uma nova anotação do gestor para um município."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO observacoes_gestor (id_municipio, status, prioridade, observacao, responsavel)
            VALUES (?, ?, ?, ?, ?)
        """, (obs.id_municipio, obs.status, obs.prioridade, obs.observacao, obs.responsavel))
        conn.commit()
        return {"mensagem": "Anotação salva com sucesso!"}
    finally:
        conn.close()

@router.put("/observacoes/{id_obs}")
def editar_observacao(id_obs: int, obs: ObservacaoUpdate):
    """Edita uma anotação existente do gestor."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE observacoes_gestor 
            SET status = COALESCE(?, status),
                prioridade = COALESCE(?, prioridade),
                observacao = COALESCE(?, observacao),
                responsavel = COALESCE(?, responsavel)
            WHERE id = ?
        """, (obs.status, obs.prioridade, obs.observacao, obs.responsavel, id_obs))
        conn.commit()
        return {"mensagem": "Anotação atualizada!"}
    finally:
        conn.close()

@router.delete("/observacoes/{id_obs}")
def deletar_observacao(id_obs: int):
    """Remove uma anotação do gestor."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM observacoes_gestor WHERE id = ?", (id_obs,))
        conn.commit()
        return {"mensagem": "Anotação removida!"}
    finally:
        conn.close()

# ==========================================
# ROTAS DOS GRÁFICOS E ANÁLISES (GET)
# ==========================================

@router.get("/top_municipios")
def get_top_municipios(limit: int = 10):
    """Retorna os N municípios mais populosos."""
    sql = """
        SELECT m.nome_municipio, e.sigla_uf as uf, p.valor as populacao
        FROM municipios m
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        ORDER BY p.valor DESC
        LIMIT ?
    """
    return query(sql, (limit,))

@router.get("/populacao_por_regiao")
def get_populacao_por_regiao():
    """Retorna a população total agrupada por região."""
    sql = """
        SELECT r.nome_regiao, SUM(p.valor) as populacao_total
        FROM regioes r
        JOIN estados e ON r.id_regiao = e.id_regiao
        JOIN municipios m ON e.id_uf = m.id_uf
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        GROUP BY r.nome_regiao
    """
    return query(sql)

@router.get("/populacao_por_estado")
def get_populacao_por_estado():
    """Retorna a população total por estado (UF)."""
    sql = """
        SELECT e.sigla_uf as uf, r.nome_regiao, SUM(p.valor) as populacao_total
        FROM estados e
        JOIN regioes r ON e.id_regiao = r.id_regiao
        JOIN municipios m ON e.id_uf = m.id_uf
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        GROUP BY e.sigla_uf, r.nome_regiao
        ORDER BY populacao_total DESC
    """
    return query(sql)

@router.get("/distribuicao_populacao")
def get_distribuicao_populacao():
    """Retorna a lista de todas as populações para montar o histograma."""
    sql = "SELECT valor FROM populacao_municipal"
    res = query(sql)
    return [r["valor"] for r in res]

@router.get("/dispersao_municipios_estado")
def get_dispersao_municipios_estado():
    """Retorna quantidade de municípios e população média por estado."""
    sql = """
        SELECT e.sigla_uf as nome_estado, r.nome_regiao, 
               COUNT(m.id_municipio) as qtd_municipios, 
               AVG(p.valor) as populacao_media
        FROM estados e
        JOIN regioes r ON e.id_regiao = r.id_regiao
        JOIN municipios m ON e.id_uf = m.id_uf
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        GROUP BY e.sigla_uf, r.nome_regiao
    """
    return query(sql)

@router.get("/heatmap_porte_regiao")
def get_heatmap_porte_regiao():
    """Retorna contagem de municípios por porte populacional e região."""
    sql = """
        SELECT r.nome_regiao,
               CASE 
                   WHEN p.valor < 20000 THEN 'Pequeno Porte'
                   WHEN p.valor BETWEEN 20000 AND 100000 THEN 'Médio Porte'
                   ELSE 'Grande Porte'
               END as porte,
               COUNT(*) as qtd
        FROM regioes r
        JOIN estados e ON r.id_regiao = e.id_regiao
        JOIN municipios m ON e.id_uf = m.id_uf
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        GROUP BY r.nome_regiao, porte
    """
    dados = query(sql)
    
    # Formata em matriz/pivot para o Heatmap
    matriz = {}
    for d in dados:
        reg = d["nome_regiao"]
        porte = d["porte"]
        qtd = d["qtd"]
        if reg not in matriz:
            matriz[reg] = {"nome_regiao": reg, "Pequeno Porte": 0, "Médio Porte": 0, "Grande Porte": 0}
        matriz[reg][porte] = qtd
        
    return list(matriz.values())