import sqlite3
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/luiz-vitor", tags=["luiz_vitor"])

DB_PATH = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class MunicipioUpdate(BaseModel):
    nome_municipio: Optional[str] = None
    id_uf: Optional[int] = None
    populacao: Optional[int] = None

class GestorCadastroCreate(BaseModel):
    id_municipio: int
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: str

class GestorCadastroUpdate(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None
    observacao: Optional[str] = None
    responsavel: Optional[str] = None

@router.get("/status")
def status():
    return {"status": "ok", "trainee": "Luiz Vitor"}

@router.get("/kpis")
def get_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_municipios = cursor.execute("SELECT COUNT(*) FROM municipios").fetchone()[0]
    total_estados = cursor.execute("SELECT COUNT(*) FROM estados").fetchone()[0]
    populacao_total = cursor.execute("SELECT SUM(valor) FROM populacao_municipal").fetchone()[0]
    ano_ref = cursor.execute("SELECT MAX(ano) FROM populacao_municipal").fetchone()[0]
    
    mais_populoso = cursor.execute("""
        SELECT m.nome_municipio, p.valor 
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        ORDER BY p.valor DESC LIMIT 1
    """).fetchone()
    
    conn.close()
    
    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total_brasil": populacao_total,
        "ano_referencia": ano_ref,
        "municipio_mais_populoso": {"nome": mais_populoso[0], "populacao": mais_populoso[1]} if mais_populoso else None
    }

@router.get("/top-municipios")
def get_top_municipios(limit: int = Query(10, description="Quantidade de municípios")):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, p.valor as populacao
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        ORDER BY p.valor DESC
        LIMIT ?
    """
    rows = cursor.execute(query, (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/populacao-regiao")
def get_populacao_regiao():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT r.nome_regiao, SUM(p.valor) as populacao_total
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        GROUP BY r.nome_regiao
        ORDER BY populacao_total DESC
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/populacao-estado")
def get_populacao_estado(regiao: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT e.sigla_uf, e.nome_uf, r.nome_regiao, SUM(p.valor) as populacao_total
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
    """
    params = []
    if regiao:
        query += " WHERE r.nome_regiao = ?"
        params.append(regiao)
    
    query += " GROUP BY e.sigla_uf, e.nome_uf, r.nome_regiao ORDER BY populacao_total DESC"
    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/distribuicao-populacao")
def get_distribuicao_populacao():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT valor FROM populacao_municipal"
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [row[0] for row in rows]

@router.get("/dispersao-estado")
def get_dispersao_estado():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT e.sigla_uf, r.nome_regiao, 
        COUNT(m.id_municipio) as qtd_municipios, 
        AVG(p.valor) as populacao_media
        FROM municipios m
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        GROUP BY e.sigla_uf, r.nome_regiao
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/heatmap-porte")
def get_heatmap_porte():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT r.nome_regiao,
        CASE 
            WHEN p.valor < 20000 THEN 'Pequeno'
            WHEN p.valor BETWEEN 20000 AND 100000 THEN 'Médio'
            ELSE 'Grande'
        END as porte,
        COUNT(*) as quantidade
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        GROUP BY r.nome_regiao, porte
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/municipios")
def criar_municipio(dados: MunicipioCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    max_id = cursor.execute("SELECT MAX(id_municipio) FROM municipios").fetchone()[0]
    novo_id = (max_id or 0) + 1
    cursor.execute("INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
                   (novo_id, dados.nome_municipio, dados.id_uf))
    cursor.execute("INSERT INTO populacao_municipal (id_municipio, ano, valor, indicador, unidade, fonte) VALUES (?, 2025, ?, 'População estimada', 'Habitantes', 'Gestor')",
                   (novo_id, dados.populacao))
    conn.commit()
    conn.close()
    return {"message": "Município criado com sucesso", "id_municipio": novo_id}

@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    existe = cursor.execute("SELECT 1 FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado")
    if dados.nome_municipio or dados.id_uf:
        cursor.execute("UPDATE municipios SET nome_municipio = COALESCE(?, nome_municipio), id_uf = COALESCE(?, id_uf) WHERE id_municipio = ?",
                       (dados.nome_municipio, dados.id_uf, id_municipio))
    if dados.populacao is not None:
        cursor.execute("UPDATE populacao_municipal SET valor = ? WHERE id_municipio = ? AND ano = 2025",
                       (dados.populacao, id_municipio))
    conn.commit()
    conn.close()
    return {"message": "Município atualizado com sucesso"}

@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    existe = cursor.execute("SELECT 1 FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado")
    cursor.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
    cursor.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    conn.commit()
    conn.close()
    return {"message": "Município removido com sucesso"}

@router.get("/cadastro-gestor")
def listar_cadastros_gestor():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT g.id_cadastro, g.id_municipio, m.nome_municipio, g.status, g.prioridade, g.observacao, g.responsavel
        FROM cadastro_gestor g
        JOIN municipios m ON g.id_municipio = m.id_municipio
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/cadastro-gestor")
def criar_cadastro_gestor(dados: GestorCadastroCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cadastro_gestor (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
    """, (dados.id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel))
    conn.commit()
    conn.close()
    return {"message": "Registro de gestor criado com sucesso"}

@router.put("/cadastro-gestor/{id_cadastro}")
def atualizar_cadastro_gestor(id_cadastro: int, dados: GestorCadastroUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    existe = cursor.execute("SELECT 1 FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cursor.execute("""
        UPDATE cadastro_gestor 
        SET status = COALESCE(?, status),
            prioridade = COALESCE(?, prioridade),
            observacao = COALESCE(?, observacao),
            responsavel = COALESCE(?, responsavel),
            data_atualizacao = CURRENT_TIMESTAMP
        WHERE id_cadastro = ?
    """, (dados.status, dados.prioridade, dados.observacao, dados.responsavel, id_cadastro))
    conn.commit()
    conn.close()
    return {"message": "Registro de gestor atualizado com sucesso"}

@router.delete("/cadastro-gestor/{id_cadastro}")
def remover_cadastro_gestor(id_cadastro: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    existe = cursor.execute("SELECT 1 FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cursor.execute("DELETE FROM cadastro_gestor WHERE id_cadastro = ?", (id_cadastro,))
    conn.commit()
    conn.close()
    return {"message": "Registro de gestor removido com sucesso"}