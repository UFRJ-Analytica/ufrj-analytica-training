from fastapi import APIRouter, HTTPException, Query, status

import sqlite3

from typing import Annotated

from app import endpoints
from app.database import query
from app.schemas import Regiao

from pydantic import BaseModel

# declarando modelos pydantic

class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int

class Municipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int

class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None

class Anotacao(BaseModel):
    id_anotacao: int
    id_municipio: int
    prioridade: int | None = None
    observacao: str
    responsavel: str

class AnotacaoCreate(BaseModel):
    prioridade: int | None = None
    observacao: str
    responsavel: str

class AnotacaoUpdate(BaseModel):
    prioridade: int | None = None
    observacao: str | None = None
    responsavel: str | None = None

# router pessoal
router = APIRouter(
        prefix="/joao-rodrigo", 
        tags=["joao_rodrigo"]
)

# rotas
@router.get("/", tags=["status"])
def root():
    return {"status": "ok", "mensagem": "API no ar. Veja /docs para a documentação."}


# ---------------------------------------------------------------------------
# Exemplo pronto, use como referência.
# ---------------------------------------------------------------------------
@router.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows

# ---------------------------------------------------------------------------
# Consulta e análise: endpoints que alimentam os gráficos do painel.
# ---------------------------------------------------------------------------

@router.get("/estados", response_model=list[Estado], tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    rows = query("SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados ORDER BY id_uf")
    return rows

@router.get("/municipios", response_model=list[Municipio], tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    """listar/buscar municípios, com filtros opcionais e paginação."""
    sql = """
        SELECT 
            id_municipio,
            nome_municipio,
            id_uf
        FROM municipios m 
    """

    params = []
    
    if nome:
        sql += " WHERE nome_municipio = ?"
        params.append(nome)
    if id_uf:
        sql += " WHERE id_uf = ?"
        params.append(id_uf)

    sql += " LIMIT ?"
    params.append(limit)

    rows = query(sql, tuple(params))

    return rows


@router.get("/populacao/top-municipios", tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    """ranking dos municípios mais populosos."""
    rows = query("""         
            SELECT m.nome_municipio, pm.valor
            FROM municipios m 
            JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio 
            ORDER BY pm.valor DESC
            LIMIT ?;
        """, (limit,))
    return rows

@router.get("/populacao/por-regiao", tags=["análise"])
def populacao_por_regiao():
    """população total agrupada por região."""
    rows = query("""
            SELECT 
                r.nome_regiao,
                SUM(pm.valor) AS populacao
            FROM municipios m 
            JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio
            JOIN estados e on m.id_uf = e.id_uf
            JOIN regioes r on e.id_regiao = r.id_regiao
            GROUP BY r.nome_regiao;
        """)
    return rows

@router.get("/populacao/por-uf", tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    """população total por estado, com filtro opcional por região."""
    sql = """
        SELECT 
            e.nome_uf,
            SUM(pm.valor) AS populacao
        FROM municipios m 
        JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio
        JOIN estados e on m.id_uf = e.id_uf
        JOIN regioes r on e.id_regiao = r.id_regiao
    """

    params = []
    
    if id_regiao:
        sql += " WHERE r.id_regiao = ?"
        params.append(id_regiao)

    sql += " GROUP BY e.nome_uf ORDER BY populacao DESC;"

    rows = query(sql, tuple(params))

    return rows

@router.get("/populacao/distribuicao", tags=["análise"])
def distribuicao_populacional():
    """valores de população de todos os municípios, para um histograma."""
    rows = query("""
            SELECT 
                FLOOR(pm.valor / 50000) * 50000 as inicio,
                FLOOR(pm.valor / 50000) * 50000 + 49999 as fim,
                COUNT(*) as quant_municipios
            FROM municipios m 
            JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio
            GROUP BY FLOOR(pm.valor/50000)
        """)
    return rows

@router.get("/populacao/dispersao-uf", tags=["análise"])
def dispersao_por_uf():
    """por estado, quantidade de municípios x população média, para um scatter."""
    rows = query("""
            SELECT 
                e.nome_uf,
                r.nome_regiao,
                COUNT(m.id_municipio) AS quant_municipios,
                SUM(pm.valor) AS populacao
            FROM estados e
            JOIN municipios m on e.id_uf = m.id_uf
            JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio
            JOIN regioes r on r.id_regiao = e.id_regiao 
            GROUP BY e.nome_uf         
        """)
    return rows

@router.get("/populacao/heatmap-regiao-porte", tags=["análise"])
def heatmap_regiao_porte():
    """quantidade de municípios por região x porte (pequeno/médio/grande),
    para um mapa de calor. Definam vocês os limites de população de cada porte."""
    rows = query("""
            WITH porte_municipios AS (
                SELECT
                    r.nome_regiao,
                    CASE 
                        WHEN pm.valor < 100000 THEN 'Pequeno'
                        WHEN pm.valor BETWEEN 100000 AND 500000 THEN 'Medio'
                        ELSE 'Grande'
                    END AS categoria
                FROM regioes r JOIN estados e on r.id_regiao = e.id_regiao 
                JOIN municipios m on e.id_uf = m.id_uf
                JOIN populacao_municipal pm on m.id_municipio = pm.id_municipio
            )
            SELECT	
                nome_regiao,
                categoria,
                COUNT(*) AS quant_municipios
            FROM porte_municipios
            GROUP BY nome_regiao, categoria;       
            """)
    return rows

@router.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    """números resumo para os KPIs do topo do painel."""
    rows = query("""
            SELECT 
                (SELECT COUNT(*) FROM municipios) as total_municipios,
                (SELECT COUNT(*) FROM estados) as total_estados,
                (SELECT pm.ano FROM populacao_municipal pm GROUP BY pm.ano LIMIT 1) as ano,
                (SELECT SUM(valor) FROM populacao_municipal) as populacao_total_br,
                (SELECT m.nome_municipio 
                 FROM municipios m 
                 JOIN populacao_municipal pm ON m.id_municipio = pm.id_municipio 
                 ORDER BY pm.valor DESC LIMIT 1) as municipio_mais_populoso
            """)

    return rows

@router.get("/municipios/{id_municipio}", response_model=Municipio, tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    """dados completos de um município, ou 404 se não existir."""
    rows = query("""
            SELECT
                id_municipio,
                nome_municipio,
                m.id_uf
            FROM municipios
            WHERE id_municipio = ?
        """, (id_municipio,))
    
    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return rows[0]

@router.post("/municipios", response_model=Municipio, tags=["dados básicos"])
def criar_municipio(dados: MunicipioCreate):
    """cadastrar um novo município (nome, estado e população inicial).
    Como não existe um id_municipio real do IBGE pra um município novo,
    gerem um (por exemplo, MAX(id_municipio) + 1)."""

    con = sqlite3.connect("database.db")
    cur = con.cursor()

    try:
        cur.execute("SELECT MAX(id_municipio) + 1 FROM municipios;")
        id_novo = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO municipios (id_municipio, nome_municipio, id_uf)
            VALUES (?, ?, ?);
        """, (id_novo, dados.nome_municipio, dados.id_uf))

        # fixando o ano em 2026 para evitar ter que importar mais bibliotecas
        cur.execute("""
            INSERT INTO populacao_municipal (id_municipio, ano, valor)
            VALUES (?, ?, ?);
        """, (id_novo, 2026, dados.populacao))

        con.commit()

        return {
            "id_municipio": id_novo,
            "nome_municipio": dados.nome_municipio,
            "id_uf": dados.id_uf,
            "populacao": dados.populacao
        }

    except Exception as e:
        con.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao inserir")
    finally:
        cur.close()
        con.close()

@router.put("/municipios/{id_municipio}", response_model=Municipio, tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    """atualizar nome, estado e/ou população de um município existente."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()

    try:
        cur.execute("SELECT 1 FROM municipios WHERE id_municipio = ?;", (id_municipio,))
        if not cur.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Município {id_municipio} não encontrado."
            )

        campos = []
        params = []

        if dados.nome_municipio is not None:
            campos.append("nome_municipio = ?")
            params.append(dados.nome_municipio)

        if dados.id_uf is not None:
            campos.append("id_uf = ?")
            params.append(dados.id_uf)

        if not campos and dados.populacao is None:
            raise HTTPException(
                status_code=400,
                detail="Nenhum campo fornecido para atualização."
            )

        if campos:
            sql = f"UPDATE municipios SET {', '.join(campos)} WHERE id_municipio = ?;"
            params.append(id_municipio)
            cur.execute(sql, params)

        if dados.populacao is not None:
            cur.execute(
                "SELECT MAX(ano) FROM populacao_municipal WHERE id_municipio = ?;",
                (id_municipio,)
            )
            max_ano = cur.fetchone()[0]

            if max_ano is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Município {id_municipio} não possui registros de população cadastrados."
                )

            cur.execute("""
                UPDATE populacao_municipal
                SET valor = ?
                WHERE id_municipio = ? AND ano = ?;
            """, (dados.populacao, id_municipio, max_ano))

        con.commit()

        cur.execute(
            "SELECT id_municipio, nome_municipio, id_uf FROM municipios WHERE id_municipio = ?;",
            (id_municipio,)
        )
        row = cur.fetchone()

        return {
            "id_municipio": row[0],
            "nome_municipio": row[1],
            "id_uf": row[2]
        }

    except HTTPException:
        raise
    except Exception as e:
        con.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        con.close()


@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    """remover um município (e os dados dependentes dele)."""
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    try:
        cur.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?;", (id_municipio,))
        
        cur.execute("DELETE FROM municipios WHERE id_municipio = ?;", (id_municipio,))

        if cur.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Município não encontrado"
            )

        con.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        con.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro ao deletar: {str(e)}"
        )
    finally:
        cur.close()
        con.close()

# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------

# o comando abaixo foi usado para criar a tabela:
def criar_tabela_anotacoes():
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    sql = """
        CREATE TABLE IF NOT EXISTS anotacao_municipal (
            id_anotacao INTEGER PRIMARY KEY,
            id_municipio INT NOT NULL,
            prioridade INT,
            observacao TEXT NOT NULL,
            responsavel TEXT,

            CONSTRAINT fk_municipio 
                FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
                
            CONSTRAINT chk_prioridade_intervalo 
                CHECK (prioridade BETWEEN 0 AND 10)
        );
    """

    cur.execute(sql)

@router.post(
        "/municipios/{id_municipio}/registros", 
        response_model=Anotacao,
        status_code=status.HTTP_201_CREATED,
        tags=["cadastro"]
)
def criar_registro(id_municipio: int, dados: AnotacaoCreate):
    """criar um novo registro de cadastro para o município."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON;")

    try:
        with con: 
            cur = con.cursor()

            cur.execute("""
                INSERT INTO anotacao_municipal (id_municipio, prioridade, observacao, responsavel)
                VALUES (?, ?, ?, ?);
            """, (id_municipio, dados.prioridade, dados.observacao, dados.responsavel))

            id_anotacao = cur.lastrowid

        return {
            "id_anotacao": id_anotacao,
            "id_municipio": id_municipio,
            "prioridade": dados.prioridade,
            "observacao": dados.observacao,
            "responsavel": dados.responsavel
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inserir")
    finally:
        cur.close()
        con.close()

@router.get("/municipios/{id_municipio}/registros", response_model=list[Anotacao], tags=["cadastro"])
def listar_registros(id_municipio: int):
    """listar os registros de cadastro de um município."""
    rows = query("""
        SELECT 
            id_anotacao,
            id_municipio,
            prioridade,
            observacao,
            responsavel
        FROM anotacao_municipal 
        WHERE id_municipio = ?
    """, (id_municipio,)) 

    return rows 

@router.put(
        "/registros/{id_registro}",
        response_model=Anotacao,
        tags=["cadastro"]
)
def atualizar_registro(id_registro: int, dados: AnotacaoUpdate):
    """atualizar um registro de cadastro existente."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON;")

    try:
        cur = con.cursor()

        campos = []
        params = []

        if dados.prioridade is not None:
            campos.append("prioridade = ?")
            params.append(dados.prioridade)

        if dados.observacao is not None:
            campos.append("observacao = ?")
            params.append(dados.observacao)

        if dados.responsavel is not None:
            campos.append("responsavel = ?")
            params.append(dados.responsavel)

        if not campos:
            raise HTTPException(
                status_code=400, 
                detail="Nenhum campo fornecido para atualização."
            )

        sql = f"UPDATE anotacao_municipal SET {', '.join(campos)} WHERE id_anotacao = ?;"
        params.append(id_registro)
        
        with con:
            cur.execute(sql, params)

        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"Registro {id_registro} não encontrado."
            )

        cur.execute(
            "SELECT id_anotacao, id_municipio, prioridade, observacao, responsavel "
            "FROM anotacao_municipal WHERE id_anotacao = ?;", 
            (id_registro,)
        )
        row = cur.fetchone()

        return {
            "id_anotacao": row[0],
            "id_municipio": row[1],
            "prioridade": row[2],
            "observacao": row[3],
            "responsavel": row[4]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {str(e)}")
    finally:
        cur.close()
        con.close()

@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    """remover um registro de cadastro."""
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    try:
        with con:
            cur.execute("DELETE FROM anotacao_municipal WHERE id_anotacao = ?;", (id_registro,))

            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Registro não encontrado"
                )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro ao deletar: {str(e)}"
        )
    finally:
        cur.close()
        con.close()
