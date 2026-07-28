import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from typing import List, Optional

class KpiResumo(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: int
    municipio_mais_populoso: str

router = APIRouter(prefix="/caroline-nomura", tags=["caroline_nomura"])

def get_db_connection():
    db_path = 'entregaveis/banco_de_dados/caroline_nomura_trainee/database.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    return conn

# Resumo dos kpis
@router.get("/kpis", response_model=KpiResumo)
def get_kpis_resumo():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM municipios")
        total_municipios = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as total FROM estados")
        total_estados = cursor.fetchone()["total"]
        
        cursor.execute("""
            SELECT SUM(valor) as pop_total, MAX(ano) as ano_ref 
            FROM populacao_municipal
        """)
        row_pop = cursor.fetchone()
        populacao_total = int(row_pop["pop_total"])
        ano_referencia = int(row_pop["ano_ref"])
        
        cursor.execute("""
            SELECT m.nome_municipio 
            FROM municipios m
            JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
            ORDER BY p.valor DESC
            LIMIT 1
        """)
        municipio_mais_populoso = cursor.fetchone()["nome_municipio"]
        
        return KpiResumo(
            total_municipios=total_municipios,
            total_estados=total_estados,
            populacao_total=populacao_total,
            ano_referencia=ano_referencia,
            municipio_mais_populoso=municipio_mais_populoso
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {str(e)}")
    finally:
        conn.close()

class MunicipioPopuloso(BaseModel):
    nome_municipio: str
    sigla_uf: str
    populacao: int

# lista de MunicipioPopuloso
@router.get("/municipios/top", response_model=List[MunicipioPopuloso])
def get_top_municipios(n: int = 10): 
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # pega nome, estado e população, limitando pelo parâmetro n
        query = """
            SELECT m.nome_municipio, e.sigla_uf, p.valor as populacao
            FROM municipios m
            JOIN estados e ON m.id_uf = e.id_uf
            JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
            ORDER BY p.valor DESC
            LIMIT ?
        """
        
        cursor.execute(query, (n,))
        linhas = cursor.fetchall()
        
        resultado = []
        for linha in linhas:
            resultado.append(
                MunicipioPopuloso(
                    nome_municipio=linha["nome_municipio"],
                    sigla_uf=linha["sigla_uf"],
                    populacao=int(linha["populacao"])
                )
            )
            
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta Top N: {str(e)}")
    finally:
        conn.close()

class PopulacaoRegiao(BaseModel):
    nome_regiao: str
    populacao_total: int

# População por região
@router.get("/regioes/populacao", response_model=List[PopulacaoRegiao])
def get_populacao_por_regiao():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # JOIN (região -> estado -> município -> populacao)
        query = """
            SELECT r.nome_regiao, SUM(p.valor) as populacao_total
            FROM regioes r
            JOIN estados e ON r.id_regiao = e.id_regiao
            JOIN municipios m ON e.id_uf = m.id_uf
            JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
            GROUP BY r.nome_regiao
            ORDER BY populacao_total DESC
        """
        
        cursor.execute(query)
        linhas = cursor.fetchall()
        
        resultado = []
        for linha in linhas:
            resultado.append(
                PopulacaoRegiao(
                    nome_regiao=linha["nome_regiao"],
                    populacao_total=int(linha["populacao_total"])
                )
            )
            
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta por região: {str(e)}")
    finally:
        conn.close()

class PopulacaoEstado(BaseModel):
    nome_uf: str
    sigla_uf: str
    populacao_total: int

# População por estado com filtro opcional
@router.get("/estados/populacao", response_model=List[PopulacaoEstado])
def get_populacao_por_estado(regiao: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT e.nome_uf, e.sigla_uf, SUM(p.valor) as populacao_total
            FROM estados e
            JOIN regioes r ON e.id_regiao = r.id_regiao
            JOIN municipios m ON e.id_uf = m.id_uf
            JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        """
        parametros = []
        
        if regiao:
            query += " WHERE r.nome_regiao = ? OR r.sigla_regiao = ?"
            parametros.extend([regiao, regiao])
            
        query += """
            GROUP BY e.nome_uf, e.sigla_uf
            ORDER BY populacao_total DESC
        """
        
        cursor.execute(query, parametros)
        linhas = cursor.fetchall()
        
        resultado = []
        for linha in linhas:
            resultado.append(
                PopulacaoEstado(
                    nome_uf=linha["nome_uf"],
                    sigla_uf=linha["sigla_uf"],
                    populacao_total=int(linha["populacao_total"])
                )
            )
            
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta por estado: {str(e)}")
    finally:
        conn.close()

class MunicipioDistribuicao(BaseModel):
    nome_municipio: str
    populacao: int

# Distribuição (histograma)
@router.get("/municipios/distribuicao", response_model=List[MunicipioDistribuicao])
def get_distribuicao_populacao():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT m.nome_municipio, p.valor as populacao
            FROM municipios m
            JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        """
        
        cursor.execute(query)
        linhas = cursor.fetchall()
        
        resultado = []
        for linha in linhas:
            resultado.append(
                MunicipioDistribuicao(
                    nome_municipio=linha["nome_municipio"],
                    populacao=int(linha["populacao"])
                )
            )
            
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta de distribuição: {str(e)}")
    finally:
        conn.close()

class DispersaoEstado(BaseModel):
    sigla_uf: str
    nome_regiao: str
    quantidade_municipios: int
    populacao_media: float

class HeatmapPorte(BaseModel):
    nome_regiao: str
    porte: str
    quantidade_municipios: int

# Gráfico de dispersão
@router.get("/estados/dispersao", response_model=List[DispersaoEstado])
def get_dispersao_estados():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # agrupa por estado, conta os municípios e calcula a média populacional
        query = """
            SELECT e.sigla_uf, r.nome_regiao,
                   COUNT(m.id_municipio) as qtd_municipios,
                   AVG(p.valor) as pop_media
            FROM estados e
            JOIN regioes r ON e.id_regiao = r.id_regiao
            JOIN municipios m ON e.id_uf = m.id_uf
            JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
            GROUP BY e.sigla_uf, r.nome_regiao
        """
        
        cursor.execute(query)
        linhas = cursor.fetchall()
        
        resultado = []
        for linha in linhas:
            resultado.append(
                DispersaoEstado(
                    sigla_uf=linha["sigla_uf"],
                    nome_regiao=linha["nome_regiao"],
                    quantidade_municipios=int(linha["qtd_municipios"]),
                    populacao_media=float(linha["pop_media"])
                )
            )
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta de dispersão: {str(e)}")
    finally:
        conn.close()

# Heatmap
@router.get("/municipios/heatmap", response_model=List[HeatmapPorte])
def get_heatmap_porte():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # CTE para classificar os municípios e depois contar
        query = """
            WITH PorteMunicipios AS (
                SELECT r.nome_regiao,
                    CASE 
                        WHEN p.valor <= 20000 THEN 'Pequeno'
                        WHEN p.valor <= 100000 THEN 'Médio'
                        ELSE 'Grande'
                    END as porte
                FROM municipios m
                JOIN estados e ON m.id_uf = e.id_uf
                JOIN regioes r ON e.id_regiao = r.id_regiao
                JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
            )
            SELECT nome_regiao, porte, COUNT(*) as quantidade_municipios
            FROM PorteMunicipios
            GROUP BY nome_regiao, porte
        """
        
        cursor.execute(query)
        linhas = cursor.fetchall()
        
        resultado = []
        for linha in linhas:
            resultado.append(
                HeatmapPorte(
                    nome_regiao=linha["nome_regiao"],
                    porte=linha["porte"],
                    quantidade_municipios=int(linha["quantidade_municipios"])
                )
            )
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta do heatmap: {str(e)}")
    finally:
        conn.close()

class AcompanhamentoInput(BaseModel):
    id_municipio: int
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None

class AcompanhamentoOutput(AcompanhamentoInput):
    id: int
    data_registro: str

# CRUD (Acompanhamentos do Gestor)

@router.post("/acompanhamentos", response_model=AcompanhamentoOutput, status_code=201)
def criar_acompanhamento(dados: AcompanhamentoInput):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (dados.id_municipio,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Município não encontrado no banco de dados.")

        query = """
            INSERT INTO acompanhamento_gestor (id_municipio, status, prioridade, observacao, responsavel)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (dados.id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel))
        conn.commit()
        
        id_inserido = cursor.lastrowid
        cursor.execute("SELECT * FROM acompanhamento_gestor WHERE id = ?", (id_inserido,))
        novo_registro = cursor.fetchone()
        
        return dict(novo_registro)
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar acompanhamento: {str(e)}")
    finally:
        conn.close()

@router.get("/acompanhamentos", response_model=List[AcompanhamentoOutput])
def listar_acompanhamentos(id_municipio: int | None = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if id_municipio:
            cursor.execute("SELECT * FROM acompanhamento_gestor WHERE id_municipio = ?", (id_municipio,))
        else:
            cursor.execute("SELECT * FROM acompanhamento_gestor")
            
        linhas = cursor.fetchall()
        return [dict(linha) for linha in linhas]
        
    finally:
        conn.close()

@router.put("/acompanhamentos/{id_acompanhamento}", response_model=AcompanhamentoOutput)
def atualizar_acompanhamento(id_acompanhamento: int, dados: AcompanhamentoInput):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            UPDATE acompanhamento_gestor 
            SET id_municipio = ?, status = ?, prioridade = ?, observacao = ?, responsavel = ?
            WHERE id = ?
        """
        cursor.execute(query, (dados.id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel, id_acompanhamento))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Acompanhamento não encontrado.")
            
        conn.commit()
        
        cursor.execute("SELECT * FROM acompanhamento_gestor WHERE id = ?", (id_acompanhamento,))
        registro_atualizado = cursor.fetchone()
        return dict(registro_atualizado)
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {str(e)}")
    finally:
        conn.close()

@router.delete("/acompanhamentos/{id_acompanhamento}")
def remover_acompanhamento(id_acompanhamento: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM acompanhamento_gestor WHERE id = ?", (id_acompanhamento,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Acompanhamento não encontrado.")
            
        conn.commit()
        return {"mensagem": "Acompanhamento removido com sucesso"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover: {str(e)}")
    finally:
        conn.close()

class MunicipioInput(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class MunicipioOutput(MunicipioInput):
    id_municipio: int

# CRUD (Municípios)

@router.post("/municipios", response_model=MunicipioOutput, status_code=201)
def criar_municipio(dados: MunicipioInput):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(id_municipio) as max_id FROM municipios")
        resultado = cursor.fetchone()
        novo_id = (resultado["max_id"] or 0) + 1
        
        cursor.execute(
            "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
            (novo_id, dados.nome_municipio, dados.id_uf)
        )
        
        cursor.execute(
            """INSERT INTO populacao_municipal 
               (id_municipio, ano, indicador, valor, unidade, fonte) 
               VALUES (?, 2025, 'População residente estimada', ?, 'pessoas', 'Cadastro Gestor')""",
            (novo_id, dados.populacao)
        )
        
        conn.commit()
        
        return MunicipioOutput(
            id_municipio=novo_id,
            nome_municipio=dados.nome_municipio,
            id_uf=dados.id_uf,
            populacao=dados.populacao
        )
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar município: {str(e)}")
    finally:
        conn.close()

@router.put("/municipios/{id_municipio}", response_model=MunicipioOutput)
def atualizar_municipio(id_municipio: int, dados: MunicipioInput):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Município não encontrado.")
            
        cursor.execute(
            "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
            (dados.nome_municipio, dados.id_uf, id_municipio)
        )
        
        cursor.execute("SELECT id_municipio FROM populacao_municipal WHERE id_municipio = ? AND ano = 2025", (id_municipio,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE populacao_municipal SET valor = ? WHERE id_municipio = ? AND ano = 2025",
                (dados.populacao, id_municipio)
            )
        else:
            cursor.execute(
                """INSERT INTO populacao_municipal 
                   (id_municipio, ano, indicador, valor, unidade, fonte) 
                   VALUES (?, 2025, 'População residente estimada', ?, 'pessoas', 'Cadastro Gestor')""",
                (id_municipio, dados.populacao)
            )
            
        conn.commit()
        
        return MunicipioOutput(
            id_municipio=id_municipio,
            nome_municipio=dados.nome_municipio,
            id_uf=dados.id_uf,
            populacao=dados.populacao
        )
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar município: {str(e)}")
    finally:
        conn.close()

@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM acompanhamento_gestor WHERE id_municipio = ?", (id_municipio,))
        
        cursor.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
        
        cursor.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Município não encontrado.")
            
        conn.commit()
        return {"mensagem": "Município e todos os seus dados dependentes foram removidos com sucesso."}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover município: {str(e)}")
    finally:
        conn.close()