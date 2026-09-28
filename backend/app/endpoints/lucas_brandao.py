import sqlite3
import os
from fastapi import APIRouter

router = APIRouter(prefix="/lucas-brandao", tags=["lucas_brandao"])

def conectar_banco():
    caminho_atual = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(caminho_atual, "../../../database.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/hello")
def hello_world():
    return {
        "mensagem": "A API está no ar.",
        "status": "ok"
    }

@router.get("/kpis")
def obter_kpis():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    #1. Total de municípios
    cursor.execute("SELECT COUNT(*) FROM municipios")
    total_municipios = cursor.fetchone()[0]
    
    #2. Total de estados
    cursor.execute("SELECT COUNT(*) FROM estados")
    total_estados = cursor.fetchone()[0]
    
    #3. População total
    cursor.execute("SELECT SUM(valor) FROM populacao_municipal")
    populacao_total = cursor.fetchone()[0]
    
    #4. Município mais populoso 
    cursor.execute("""
        SELECT m.NOME_MUNICIPIO, p.VALOR 
        FROM municipios m
        JOIN populacao_municipal p ON m.ID_MUNICIPIO = p.ID_MUNICIPIO
        ORDER BY p.VALOR DESC
        LIMIT 1
    """)
    resultado_populoso = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "nome_mais_populoso": resultado_populoso["NOME_MUNICIPIO"],
        "populacao_mais_populoso": resultado_populoso["VALOR"]
    }