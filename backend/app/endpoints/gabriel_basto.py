import os
import sqlite3
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/gabriel-basto", tags=["gabriel_basto"])

import os
import sqlite3
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(prefix="/gabriel-basto", tags=["gabriel_basto"])

def find_database():
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    db_path = os.path.join(base_dir, "entregaveis", "banco_de_dados", "gabriel_basto_trainee", "database.db")
    
    if os.path.exists(db_path):
        return db_path
    
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while current_dir != os.path.dirname(current_dir):
        possible_path = os.path.join(current_dir, "entregaveis", "banco_de_dados", "gabriel_basto_trainee", "database.db")
        if os.path.exists(possible_path):
            return possible_path
        current_dir = os.path.dirname(current_dir)
        
    return "database.db"

DB_PATH = find_database()
print(f"--> Usando banco de dados em: {DB_PATH}") # Vai imprimir o caminho no terminal para você confirmar

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Criar a tabela de anotações caso não exista
    conn.execute("""
        CREATE TABLE IF NOT EXISTS anotacoes_gestor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_municipio INTEGER NOT NULL,
            status TEXT,
            prioridade TEXT,
            observacao TEXT,
            responsavel TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio)
        )
    """)
    conn.commit()
    return conn

# --- SCHEMAS PYDANTIC ---
class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class MunicipioUpdate(BaseModel):
    nome_municipio: Optional[str] = None
    id_uf: Optional[int] = None
    populacao: Optional[int] = None

class AnotacaoCreate(BaseModel):
    id_municipio: int
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: Optional[str] = None

class AnotacaoUpdate(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None
    observacao: Optional[str] = None
    responsavel: Optional[str] = None

# --- PARTE 1: ENDPOINTS DE CONSULTA E ANÁLISE ---

@router.get("/kpis")
def get_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM municipios")
    total_municipios = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM estados")
    total_estados = cursor.fetchone()[0]
    
    # Busca a soma da população na tabela fato (assumindo indicador de população = 1)
    cursor.execute("SELECT SUM(valor) FROM fato_indicador_municipal WHERE id_indicador = 1")
    populacao_total = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT m.nome_municipio, f.valor as populacao 
        FROM fato_indicador_municipal f 
        JOIN municipios m ON f.id_municipio = m.id_municipio 
        WHERE f.id_indicador = 1
        ORDER BY f.valor DESC LIMIT 1
    """)
    mais_populoso = cursor.fetchone()
    
    conn.close()
    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": 2025,
        "municipio_mais_populoso": mais_populoso["nome_municipio"] if mais_populoso else "N/A",
        "populacao_mais_populoso": mais_populoso["populacao"] if mais_populoso else 0
    }

@router.get("/top-municipios")
def get_top_municipios(n: int = Query(10, ge=1, le=100)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.nome_municipio, e.sigla_uf, f.valor as populacao 
        FROM fato_indicador_municipal f 
        JOIN municipios m ON f.id_municipio = m.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        WHERE f.id_indicador = 1
        ORDER BY f.valor DESC LIMIT ?
    """, (n,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/populacao-regiao")
def get_populacao_regiao():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.nome_regiao, SUM(f.valor) as populacao_total 
        FROM fato_indicador_municipal f 
        JOIN municipios m ON f.id_municipio = m.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        JOIN regioes r ON e.id_regiao = r.id_regiao 
        WHERE f.id_indicador = 1
        GROUP BY r.nome_regiao 
        ORDER BY populacao_total DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/populacao-estado")
def get_populacao_estado(regiao_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT e.sigla_uf, SUM(f.valor) as populacao_total 
        FROM fato_indicador_municipal f 
        JOIN municipios m ON f.id_municipio = m.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        WHERE f.id_indicador = 1
    """
    params = []
    if regiao_id is not None and regiao_id > 0:
        query += " AND e.id_regiao = ? "
        params.append(regiao_id)
    
    query += " GROUP BY e.sigla_uf ORDER BY populacao_total DESC "
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/distribuicao-populacao")
def get_distribuicao_populacao():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT valor as populacao FROM fato_indicador_municipal WHERE id_indicador = 1")
    rows = cursor.fetchall()
    conn.close()
    return [row["populacao"] for row in rows]

@router.get("/dispersao-estado")
def get_dispersao_estado():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.sigla_uf, r.nome_regiao, COUNT(m.id_municipio) as qtd_municipios, AVG(f.valor) as populacao_media 
        FROM municipios m 
        JOIN fato_indicador_municipal f ON m.id_municipio = f.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        JOIN regioes r ON e.id_regiao = r.id_regiao 
        WHERE f.id_indicador = 1
        GROUP BY e.id_uf, e.sigla_uf, r.nome_regiao
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/heatmap-porte")
def get_heatmap_porte():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.nome_regiao, 
               CASE 
                   WHEN f.valor < 20000 THEN 'Pequeno (<20k)' 
                   WHEN f.valor BETWEEN 20000 AND 100000 THEN 'Médio (20k-100k)' 
                   ELSE 'Grande (>100k)' 
               END AS porte, 
               COUNT(*) as quantidade 
        FROM fato_indicador_municipal f 
        JOIN municipios m ON f.id_municipio = m.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        JOIN regioes r ON e.id_regiao = r.id_regiao 
        WHERE f.id_indicador = 1
        GROUP BY r.nome_regiao, porte
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- PARTE 2: CRUD DE MUNICÍPIOS ---

@router.get("/municipios-lista")
def list_municipios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, f.valor as populacao 
        FROM municipios m 
        LEFT JOIN estados e ON m.id_uf = e.id_uf 
        LEFT JOIN fato_indicador_municipal f ON m.id_municipio = f.id_municipio AND f.id_indicador = 1
        ORDER BY m.nome_municipio ASC LIMIT 500
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/municipios", status_code=status.HTTP_201_CREATED)
def create_municipio(data: MunicipioCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id_municipio) FROM municipios")
    max_id = cursor.fetchone()[0]
    new_id = (max_id or 0) + 1
    
    try:
        cursor.execute(
            "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
            (new_id, data.nome_municipio, data.id_uf)
        )
        
        cursor.execute(
            "INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor) VALUES (?, ?, ?, ?)",
            (new_id, 1, 2025, data.populacao)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")
        
    conn.close()
    return {"id_municipio": new_id, "mensagem": "Município criado com sucesso!"}

@router.put("/municipios/{id_municipio}")
def update_municipio(id_municipio: int, data: MunicipioUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado.")
    
    if data.nome_municipio or data.id_uf:
        updates = []
        params = []
        if data.nome_municipio:
            updates.append("nome_municipio = ?")
            params.append(data.nome_municipio)
        if data.id_uf:
            updates.append("id_uf = ?")
            params.append(data.id_uf)
        params.append(id_municipio)
        cursor.execute(f"UPDATE municipios SET {', '.join(updates)} WHERE id_municipio = ?", params)
        
    if data.populacao is not None:
        cursor.execute("UPDATE fato_indicador_municipal SET valor = ? WHERE id_municipio = ? AND id_indicador = 1", (data.populacao, id_municipio))
        
    conn.commit()
    conn.close()
    return {"mensagem": "Município atualizado com sucesso!"}

@router.delete("/municipios/{id_municipio}")
def delete_municipio(id_municipio: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fato_indicador_municipal WHERE id_municipio = ?", (id_municipio,))
    cursor.execute("DELETE FROM anotacoes_gestor WHERE id_municipio = ?", (id_municipio,))
    cursor.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    conn.commit()
    conn.close()
    return {"mensagem": "Município removido com sucesso!"}

# --- PARTE 3: CRUD DE ANOTAÇÕES DO GESTOR  ---

@router.get("/anotacoes")
def list_anotacoes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, m.nome_municipio 
        FROM anotacoes_gestor a 
        JOIN municipios m ON a.id_municipio = m.id_municipio 
        ORDER BY a.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.post("/anotacoes", status_code=status.HTTP_201_CREATED)
def create_anotacao(data: AnotacaoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO anotacoes_gestor (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
    """, (data.id_municipio, data.status, data.prioridade, data.observacao, data.responsavel))
    conn.commit()
    conn.close()
    return {"mensagem": "Anotação registrada com sucesso!"}

@router.put("/anotacoes/{anotacao_id}")
def update_anotacao(anotacao_id: int, data: AnotacaoUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM anotacoes_gestor WHERE id = ?", (anotacao_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Anotação não encontrada.")
    
    updates = []
    params = []
    if data.status:
        updates.append("status = ?")
        params.append(data.status)
    if data.prioridade:
        updates.append("prioridade = ?")
        params.append(data.prioridade)
    if data.observacao is not None:
        updates.append("observacao = ?")
        params.append(data.observacao)
    if data.responsavel is not None:
        updates.append("responsavel = ?")
        params.append(data.responsavel)
        
    if updates:
        params.append(anotacao_id)
        cursor.execute(f"UPDATE anotacoes_gestor SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        
    conn.close()
    return {"mensagem": "Anotação atualizada com sucesso!"}

@router.delete("/anotacoes/{anotacao_id}")
def delete_anotacao(anotacao_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anotacoes_gestor WHERE id = ?", (anotacao_id,))
    conn.commit()
    conn.close()
    return {"mensagem": "Anotação removida com sucesso!"}