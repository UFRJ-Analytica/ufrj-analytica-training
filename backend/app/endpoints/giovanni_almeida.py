from fastapi import APIRouter, Query, HTTPException
from app.database import query, get_connection
from app.schemas import Regiao
from pydantic import BaseModel
from pathlib import Path
import app.database


#Checar se está atualizando corretamente, se os filtros estão bem aplicados/poderiam ser melhor,
#E entreggar
app.database.DB_PATH= Path(__file__).resolve().parent.parent.parent.parent/"entregaveis"/"banco_de_dados"/"giovanni_almeida_trainee"/"database.db"
""" Antes de tudo, função gerenciadora de DB para garantir que possa ter transações"""
def execute_transaction(statements: list[tuple[str, dict]]) -> None:
    """Executa uma lista de instruções de escrita garantindo a efetivação (commit)."""
    conn = get_connection()
    try:
        # A execução ocorre sequencialmente no mesmo cursor
        for sql, params in statements:
            conn.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

"""Aqui, os formatos validados de resposta:"""
class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str

class Municipio(BaseModel):
    id_municipio: int
    nome_municipio: str

class Populacao_Municipal(BaseModel):
    ano: int
    valor: int

class MunPop(BaseModel):
    nome_municipio: str
    valor_populacao: int

class RegPop(BaseModel):
    nome_regiao: str
    valor_populacao: int

class UfPop(BaseModel):
    nome_uf: str
    valor_populacao: int

class Estadostats(BaseModel):
    nome_uf: str
    avg_populacao: float
    numero_municipios: int 

class RegiaoPorte(BaseModel):
    nome_regiao: str
    nome_porte: str
    numero_municipios: int

class KPIS(BaseModel):
    numero_municipios: int
    numero_estados: int
    populacao_total: int
    municipio_mais_populoso: str
    ano_ref:int
class RegistroGestorCreate(BaseModel):
    status: str
    prioridade: str
    responsavel: str | None = None
    observacao: str | None = None

class RegistroGestorResponse(BaseModel):
    id_registro: int
    id_municipio: int
    status: str
    prioridade: str
    responsavel: str | None
    observacao: str | None
    data_registro: str

#Formato do payload de criação de municipio
class MunicipioCreate(BaseModel):
    nome_municipio: str
    nome_estado: str
    populacao: int
#Formato de payload de atualização de município
class MunicipioUpdate(BaseModel):
    novo_nome: str | None = None
    novo_estado: str | None = None
    nova_pop: int | None = None


router = APIRouter(prefix="/giovanni-almeida", tags=["giovanni_almeida"])

@router.get("/status")
def status():
    return {"status": "Ok"}



@router.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows


# ---------------------------------------------------------------------------
# Consulta e análise: endpoints que alimentam os gráficos do painel.
# ---------------------------------------------------------------------------

@router.get("/estados", response_model=list[Estado], tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    """TODO: listar estados, com filtro opcional por região."""
    if id_regiao is None:
        sql_string = "SELECT id_uf, sigla_uf, nome_uf FROM estados"
        return query(sql_string)
    
    sql_string = "SELECT id_uf, sigla_uf, nome_uf FROM estados WHERE id_regiao = :id_regiao"
    return query(sql_string, {"id_regiao": id_regiao})

@router.get("/municipios", response_model=list[Municipio], tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    sql_selection = "SELECT id_municipio, nome_municipio FROM municipios"
    
    condicoes = []
    parametros = {"limit": limit}

    if id_uf is not None:
        condicoes.append("id_uf = :id_uf")
        parametros["id_uf"] = id_uf    
    if nome is not None:
        condicoes.append("nome_municipio = :nome")
        parametros["nome"] = nome
    if condicoes:
        sql_string = f"{sql_selection} WHERE " + " AND ".join(condicoes)
    else:
        sql_string = sql_selection

    sql_string += " LIMIT :limit"
    return query(sql_string, parametros)

@router.get("/populacao/top-municipios", response_model=list[MunPop], tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    """TODO: ranking dos municípios mais populosos."""
    sql_selection = """
        SELECT m.nome_municipio, p.valor AS valor_populacao 
        FROM municipios m
        INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
        ORDER BY p.valor DESC
    """
    sql_string = sql_selection + " LIMIT :limit"
    parametros = {"limit": limit}
    return query(sql_string, parametros)


@router.get("/populacao/por-regiao", response_model=list[RegPop], tags=["análise"])
def populacao_por_regiao():
    """TODO: população total agrupada por região."""
    # Correção: SUM(p.valor) alterado para valor_populacao
    sql_selection = """
        SELECT SUM(p.valor) AS valor_populacao, r.nome_regiao 
        FROM regioes r 
        INNER JOIN estados e ON r.id_regiao = e.id_regiao
        INNER JOIN municipios m ON e.id_uf = m.id_uf
        INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        GROUP BY r.nome_regiao
    """
    return query(sql_selection)


@router.get("/populacao/por-uf", response_model=list[UfPop], tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    """TODO: população total por estado, com filtro opcional por região."""
    # Correção: SUM(p.valor) alterado para valor_populacao
    if id_regiao is None:
        sql_selection = """
            SELECT SUM(p.valor) AS valor_populacao, e.nome_uf 
            FROM estados e
            INNER JOIN municipios m ON e.id_uf = m.id_uf
            INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
            GROUP BY e.nome_uf
        """
        return query(sql_selection)
    else:
        sql_selection = """
            SELECT SUM(p.valor) AS valor_populacao, e.nome_uf 
            FROM estados e
            INNER JOIN municipios m ON e.id_uf = m.id_uf
            INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        """
        parametros = {"id_regiao" : id_regiao}
        condicoes = ["e.id_regiao = :id_regiao"]
        sql_string = f"{sql_selection} WHERE " + " AND ".join(condicoes) + " GROUP BY e.nome_uf"
        return query(sql_string, parametros)


@router.get("/populacao/distribuicao", response_model=list[MunPop], tags=["análise"])
def distribuicao_populacional():
    """TODO: valores de população de todos os municípios, para um histograma."""
    sql_selection = """
        SELECT SUM(p.valor) AS valor_populacao, m.nome_municipio 
        FROM municipios m  
        INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
        GROUP BY m.nome_municipio
    """
    return query(sql_selection)


@router.get("/populacao/dispersao-uf", response_model=list[Estadostats], tags=["análise"])
def dispersao_por_uf():
    """TODO: por estado, quantidade de municípios x população média, para um scatter."""
    sql_selection = """
        SELECT 
            COUNT(m.id_municipio) AS numero_municipios, 
            AVG(p.valor) AS avg_populacao, 
            e.nome_uf  
        FROM municipios m  
        INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
        INNER JOIN estados e ON m.id_uf = e.id_uf   
        GROUP BY e.nome_uf
    """
    return query(sql_selection)


@router.get("/populacao/heatmap-regiao-porte", response_model=list[RegiaoPorte], tags=["análise"])
def heatmap_regiao_porte():
    """TODO: quantidade de municípios por região x porte (pequeno/médio/grande), para um mapa de calor."""
    sql_selection = """
        SELECT 
            CASE 
                WHEN p.valor >= 250000 THEN 'Grande'
                WHEN p.valor >= 75000 THEN 'Medio'
                ELSE 'Pequeno'
            END AS nome_porte,
            COUNT(m.id_municipio) AS numero_municipios,
            r.nome_regiao
        FROM municipios m 
        INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        INNER JOIN estados e ON m.id_uf = e.id_uf
        INNER JOIN regioes r ON e.id_regiao = r.id_regiao
        GROUP BY  r.nome_regiao, nome_porte
    """
    return query(sql_selection)


@router.get("/estatisticas/resumo", response_model=KPIS, tags=["análise"])
def resumo_estatistico():
    """TODO: números resumo para os KPIs do topo do painel."""
    sql_selection = """
        SELECT
            (SELECT COUNT(*) FROM municipios) AS numero_municipios,
            (SELECT COUNT(*) FROM estados) AS numero_estados,
            (SELECT SUM(valor) FROM populacao_municipal) AS populacao_total,
            (
                SELECT m.nome_municipio 
                FROM municipios m 
                INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
                ORDER BY p.valor DESC 
                LIMIT 1
            ) AS municipio_mais_populoso,
            (SELECT MAX(ano)FROM populacao_municipal) AS ano_ref
    """
    resultado = query(sql_selection)
    if resultado:
        return resultado[0]
    raise HTTPException(status_code=404, detail="Dados não encontrados")

@router.get("/municipios/namesearch", response_model=list[Municipio], tags=["dados básicos"])
def detalhe_municipio_nome(nome_municipio: str):
    """Retorna os dados básicos de um município baseado no nome exato."""
    parameter = {"nome_municipio": nome_municipio}
    condicao = ["m.nome_municipio = :nome_municipio"]
    
    sql_selection = """
        SELECT m.id_municipio, m.nome_municipio
        FROM municipios m 
    """
    sql_condition = f"{sql_selection} WHERE " + " AND ".join(condicao)
    result = query(sql_condition, parameter)
    
    if not result:
        raise HTTPException(status_code=404, detail="Não existe tal município")
    return result

@router.get("/municipios/{id_municipio}", response_model=list[MunPop], tags=["dados básicos"])
def detalhe_municipio_id(id_municipio: int):
    """Retorna o detalhamento (nome e população) de um município pelo ID."""
    parameter = {"id_municipio": id_municipio}
    condicao = ["m.id_municipio = :id_municipio"]
    
    sql_selection = """
        SELECT m.nome_municipio, p.valor AS valor_populacao 
        FROM municipios m 
        INNER JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
    """
    sql_condition = f"{sql_selection} WHERE " + " AND ".join(condicao)
    result = query(sql_condition, parameter)
    
    if not result:
        raise HTTPException(status_code=404, detail="Não existe tal município")
    return result


@router.post("/municipios", tags=["dados básicos"])
def criar_municipio(payload: MunicipioCreate):
    """Cadastra um novo município (nome, estado e população inicial)."""
    parametros = {
        "nome_municipio": payload.nome_municipio,
        "nome_estado": payload.nome_estado,
        "populacao": payload.populacao
    }

    sql_insert_municipio = """
        INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
        SELECT 
            (SELECT COALESCE(MAX(id_municipio), 0) + 1 FROM municipios), 
            :nome_municipio, 
            id_uf 
        FROM estados 
        WHERE nome_uf = :nome_estado;
    """
    sql_insert_populacao = """
        INSERT INTO populacao_municipal (id_municipio, ano, valor)
        SELECT 
            (SELECT MAX(id_municipio) FROM municipios),
            (SELECT MAX(ano) FROM populacao_municipal),
            :populacao;
    """
    transactions = [(sql_insert_municipio, parametros), (sql_insert_populacao, parametros)]
    try:
        execute_transaction(transactions)
        return {"status": "Criação feita com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha na transação: {str(e)}")


@router.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(
    id_municipio: int, 
    payload: MunicipioUpdate
):
    """Atualiza nome, estado e/ou população de um município existente."""
    parametros = {
        "id_municipio": id_municipio, 
        "novo_nome": payload.novo_nome, 
        "novo_estado": payload.novo_estado, 
        "nova_pop": payload.nova_pop
    }
    
    transacao = []
    condicoes = []
    
    if payload.novo_estado is not None:
        condicoes.append("id_uf = (SELECT id_uf FROM estados WHERE nome_uf = :novo_estado)")

    if payload.novo_nome is not None:
        condicoes.append("nome_municipio = :novo_nome")
        
    if condicoes:
        sql_update_municipio = "UPDATE municipios SET " + ", ".join(condicoes) + " WHERE id_municipio = :id_municipio"
        transacao.append((sql_update_municipio, parametros))
        
    if payload.nova_pop is not None:
        sql_update_pop = """
            UPDATE populacao_municipal
            SET valor = :nova_pop
            WHERE id_municipio = :id_municipio
        """
        transacao.append((sql_update_pop, parametros))
        
    if not transacao:
        raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

    try:
        execute_transaction(transacao)
        return {"status": "Atualização feita com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha na atualização: {str(e)}")
    
@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    """Remove um município (e os dados dependentes dele)."""
    parametros = {"id_municipio": id_municipio}
    sql_deletion_pop = "DELETE FROM populacao_municipal WHERE id_municipio = :id_municipio"
    sql_deletion_municipios = "DELETE FROM municipios WHERE id_municipio = :id_municipio"
    transacao = [
        (sql_deletion_pop, parametros),
        (sql_deletion_municipios, parametros)
    ]
    try:
        execute_transaction(transacao)
        return {"status": "Remoção feita com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha na remoção: {str(e)}")# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------
#Criar a tabela: DELETE CASCADE pra caso seja tirado o id_municipio das tabelas originais
def inicializar_tabela_gestor():
    ddl_script = """
    CREATE TABLE IF NOT EXISTS registros_gestor (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_municipio INTEGER NOT NULL,
        status TEXT NOT NULL,
        prioridade TEXT NOT NULL,
        responsavel TEXT,
        observacao TEXT,
        data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_municipio 
            FOREIGN KEY (id_municipio) 
            REFERENCES municipios (id_municipio) 
            ON DELETE CASCADE
    );
        """
    
    # Executa a instrução empacotada na tupla com um dicionário vazio
    try:
        execute_transaction([(ddl_script, {})])
        print("Tabela 'registros_gestor' estruturada com sucesso.")
    except Exception as e:
        print(f"Falha na execução do DDL: {e}")

@router.post("/municipios/{id_municipio}/registros", tags=["cadastro"])
def criar_registro(id_municipio: int, payload: RegistroGestorCreate):
    """Cria um novo registro de cadastro gerencial para o município."""
    parametros = payload.model_dump()
    parametros["id_municipio"] = id_municipio
    
    sql_insert = """
        INSERT INTO registros_gestor (id_municipio, status, prioridade, responsavel, observacao)
        VALUES (:id_municipio, :status, :prioridade, :responsavel, :observacao)
    """
    try:
        execute_transaction([(sql_insert, parametros)])
        return {"status": "Registro criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha na criação do registro: {str(e)}")


@router.get("/municipios/{id_municipio}/registros", response_model=list[RegistroGestorResponse], tags=["cadastro"])
def listar_registros(id_municipio: int):
    """Lista os registros de cadastro de um município específico."""
    
    sql_selection = """
        SELECT id_registro, id_municipio, status, prioridade, responsavel, observacao, data_registro 
        FROM registros_gestor 
        WHERE id_municipio = :id_municipio
        ORDER BY data_registro DESC
    """
    
    return query(sql_selection, {"id_municipio": id_municipio})


@router.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, payload: RegistroGestorCreate):
    """Atualiza o conteúdo de um registro de cadastro existente."""
    
    parametros = payload.model_dump()
    parametros["id_registro"] = id_registro
    
    sql_update = """
        UPDATE registros_gestor 
        SET 
            status = :status, 
            prioridade = :prioridade, 
            responsavel = :responsavel, 
            observacao = :observacao 
        WHERE id_registro = :id_registro
    """
    
    try:
        execute_transaction([(sql_update, parametros)])
        return {"status": "Registro atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha na atualização do registro: {str(e)}")


@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    """Remove definitivamente um registro de cadastro gerencial."""
    
    sql_delete = "DELETE FROM registros_gestor WHERE id_registro = :id_registro"
    
    try:
        execute_transaction([(sql_delete, {"id_registro": id_registro})])
        return {"status": "Registro removido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha na remoção do registro: {str(e)}")
if __name__ == "__main__":
    inicializar_tabela_gestor()