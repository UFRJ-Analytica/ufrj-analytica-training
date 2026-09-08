from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import *
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/luiz-conti", tags=["luiz_conti"])

#Funções de acesso ao database foram colocadas aqui para conseguir acessar o meu database feito na atividade de BD1
#sem precisar alterar o database.py

def get_connection() -> sqlite3.Connection:
    """Abre uma conexão com o SQLite configurada para retornar dicts (Row)."""
    conn = sqlite3.connect(r"entregaveis\banco_de_dados\luiz_conti_trainee\database.db")
    conn.row_factory = sqlite3.Row
    return conn


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Executa uma query e retorna uma lista de dicts. Faz commit para persistir INSERT/UPDATE/DELETE."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

#Schemas foram colocados aqui para evitar conflitos com outros trainees no schemas.py

class Resumo(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: int
    municipio_mais_populoso: str


class MunicipioRanking(BaseModel):
    nome_municipio: str
    populacao: int


class PopulacaoRegiao(BaseModel):
    nome_regiao: str
    populacao: int


class PopulacaoEstado(BaseModel):
    sigla_uf: str
    nome_uf: str
    populacao: int


class DistribuicaoMunicipio(BaseModel):
    populacao: int


class DispersaoEstado(BaseModel):
    sigla_uf: str
    nome_regiao: str
    quantidade_municipios: int
    populacao_media: float


class HeatmapPorte(BaseModel):
    nome_regiao: str
    porte: str
    quantidade_municipios: int


class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int

class Regiao(BaseModel):
    id_regiao: int
    nome_regiao: str


class MunicipioResumo(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int


class MunicipioDetalhe(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int
    ano: int
    fonte: str

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int
    ano: int
    fonte: str


class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None
    fonte: str | None = None


class Cadastro(BaseModel):
    id_cadastro: int
    id_municipio: int
    status: str
    prioridade: str
    observacao: str
    responsavel: str


class CadastroCreate(BaseModel):
    id_municipio: int
    status: str
    prioridade: str
    observacao: str
    responsavel: str


class CadastroUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None


@router.get("/status")
def status():
    return {"status": "ok"}

# -------------------#
# Consulta/Análise
# -------------------#

@router.get("/estados", response_model=list[Estado])
def listar_estados(id_regiao: int | None = Query(default=None)):
    filtro = f"WHERE id_regiao = {id_regiao}" if id_regiao else ""
    response = query(f"""
        SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados
            {filtro}
            ORDER BY nome_uf
            """)
    return response


@router.get("/municipios", response_model=list[MunicipioResumo])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    filtros = []
    if nome:
        filtros.append(f"nome_municipio LIKE '%{nome}%'")
    if id_uf:
        filtros.append(f"id_uf = {id_uf}")
    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    response = query(f"""
        SELECT id_municipio, nome_municipio, id_uf FROM municipios
            {where}
            ORDER BY nome_municipio
            LIMIT {limit}
            """)
    return response

@router.get("/regioes", response_model=list[Regiao])
def listar_regioes():
    response = query("SELECT id_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return response

@router.get("/populacao/top-municipios", response_model=list[MunicipioRanking])
def top_municipios(limit: int = Query(default=10, le=100)):
    response = query(f"""
        SELECT nome_municipio, valor AS populacao
            FROM municipios
            JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
            JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
            WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
            ORDER BY valor DESC LIMIT {limit}
            """)
    return response


@router.get("/populacao/por-regiao", response_model=list[PopulacaoRegiao])
def populacao_por_regiao():
    response = query("""
        SELECT nome_regiao, SUM(valor) AS populacao
            FROM regioes
            JOIN estados ON regioes.id_regiao = estados.id_regiao
            JOIN municipios ON estados.id_uf = municipios.id_uf
            JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
            JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
            WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
            GROUP BY regioes.id_regiao
            ORDER BY populacao DESC
            """)
    return response


@router.get("/populacao/por-uf", response_model=list[PopulacaoEstado])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    filtro = f"AND estados.id_regiao = {id_regiao}" if id_regiao else ""
    response = query(f"""
        SELECT sigla_uf, nome_uf, SUM(valor) AS populacao
            FROM estados
            JOIN municipios ON estados.id_uf = municipios.id_uf
            JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
            JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
            WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
            {filtro}
            GROUP BY estados.id_uf
            ORDER BY populacao DESC
            """)
    return response


@router.get("/populacao/distribuicao", response_model=list[DistribuicaoMunicipio])
def distribuicao_populacional():
    response = query("""
        SELECT valor AS populacao
            FROM fato_indicador_municipal
            JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
            WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
        """)
    return response


@router.get("/populacao/dispersao-uf", response_model=list[DispersaoEstado])
def dispersao_por_uf():
    response = query("""
        SELECT sigla_uf, nome_regiao, COUNT(municipios.id_municipio) AS quantidade_municipios, AVG(valor) AS populacao_media
            FROM estados
            JOIN regioes ON estados.id_regiao = regioes.id_regiao
            JOIN municipios ON municipios.id_uf = estados.id_uf
            JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
            JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
            WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
            GROUP BY estados.id_uf
            """)
    return response


@router.get("/populacao/heatmap-regiao-porte", response_model=list[HeatmapPorte])
def heatmap_regiao_porte():
    response = query("""
        SELECT nome_regiao, porte, COUNT(*) AS quantidade_municipios
            FROM (
                SELECT municipios.id_municipio, estados.id_regiao AS id_regiao,
                    CASE
                        WHEN valor < 20000 THEN 'Pequeno'
                        WHEN valor < 100000 THEN 'Médio'
                        ELSE 'Grande'
                    END AS porte
                FROM municipios
                JOIN estados ON municipios.id_uf = estados.id_uf
                JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
                JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
                WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
            ) AS sub
            JOIN regioes ON regioes.id_regiao = sub.id_regiao
            GROUP BY nome_regiao, porte
            """)
    return response


@router.get("/estatisticas/resumo", response_model=Resumo)
def resumo_estatistico():
    response = query("""
        SELECT
            (SELECT COUNT(*) FROM municipios) AS total_municipios,
            (SELECT COUNT(*) FROM estados) AS total_estados,
            (SELECT SUM(valor) FROM fato_indicador_municipal
                JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
                WHERE indicadores.nome_indicador = 'populacao_residente_estimada') AS populacao_total,
            (SELECT MAX(ano) FROM fato_indicador_municipal
                JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
                WHERE indicadores.nome_indicador = 'populacao_residente_estimada') AS ano_referencia,
            (SELECT nome_municipio FROM municipios
                JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
                JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
                WHERE indicadores.nome_indicador = 'populacao_residente_estimada'
                ORDER BY valor DESC LIMIT 1) AS municipio_mais_populoso
    """)[0]
    return response


@router.get("/municipios/{id_municipio}", response_model=MunicipioDetalhe)
def detalhe_municipio(id_municipio: int):
    response = query(f"""
        SELECT municipios.id_municipio, nome_municipio, id_uf, valor AS populacao, ano, fonte
            FROM municipios
            JOIN fato_indicador_municipal ON fato_indicador_municipal.id_municipio = municipios.id_municipio
            JOIN indicadores ON indicadores.id_indicador = fato_indicador_municipal.id_indicador
            WHERE municipios.id_municipio = {id_municipio}
                AND indicadores.nome_indicador = 'populacao_residente_estimada'
            """)
    if not response:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return response[0]

@router.post("/municipios", response_model=MunicipioResumo)
def criar_municipio(municipio: MunicipioCreate):
    novo_id = query("SELECT MAX(id_municipio) AS max_id FROM municipios")[0]["max_id"] + 1
    id_indicador = query(
        "SELECT id_indicador FROM indicadores WHERE nome_indicador = 'populacao_residente_estimada'"
    )[0]["id_indicador"]

    query("INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
          (novo_id, municipio.nome_municipio, municipio.id_uf))
    query("""
        INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor, fonte)
        VALUES (?, ?, ?, ?, ?)
        """, (novo_id, id_indicador, municipio.ano, municipio.populacao, municipio.fonte))

    return {"id_municipio": novo_id, "nome_municipio": municipio.nome_municipio, "id_uf": municipio.id_uf}


@router.put("/municipios/{id_municipio}", response_model=MunicipioDetalhe)
def atualizar_municipio(id_municipio: int, municipio: MunicipioUpdate):
    existente = query("SELECT * FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    if municipio.nome_municipio is not None:
        query("UPDATE municipios SET nome_municipio = ? WHERE id_municipio = ?",
              (municipio.nome_municipio, id_municipio))
    if municipio.id_uf is not None:
        query("UPDATE municipios SET id_uf = ? WHERE id_municipio = ?",
              (municipio.id_uf, id_municipio))
    if municipio.populacao is not None:
        query("""
            UPDATE fato_indicador_municipal SET valor = ?
            WHERE id_municipio = ?
                AND id_indicador = (SELECT id_indicador FROM indicadores WHERE nome_indicador = 'populacao_residente_estimada')
            """, (municipio.populacao, id_municipio))
    if municipio.fonte is not None:
        query("""
            UPDATE fato_indicador_municipal SET fonte = ?
            WHERE id_municipio = ?
                AND id_indicador = (SELECT id_indicador FROM indicadores WHERE nome_indicador = 'populacao_residente_estimada')
            """, (municipio.fonte, id_municipio))

    return detalhe_municipio(id_municipio)


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    existente = query("SELECT * FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not existente:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    query("DELETE FROM fato_indicador_municipal WHERE id_municipio = ?", (id_municipio,))
    query("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    return {"detail": "Município removido"}

# -------------------#
# Cadastro
# -------------------#

@router.post("/cadastro", response_model=Cadastro)
def criar_cadastro(cadastro: CadastroCreate):
    query("""
        INSERT INTO cadastro (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
        """, (cadastro.id_municipio, cadastro.status, cadastro.prioridade, cadastro.observacao, cadastro.responsavel))

    novo = query("SELECT * FROM cadastro WHERE id_cadastro = (SELECT MAX(id_cadastro) FROM cadastro)")[0]
    return novo


@router.get("/cadastro", response_model=list[Cadastro])
def listar_cadastro(id_municipio: int | None = Query(default=None)):
    if id_municipio:
        return query("SELECT * FROM cadastro WHERE id_municipio = ?", (id_municipio,))
    return query("SELECT * FROM cadastro")


@router.put("/cadastro/{id_cadastro}", response_model=Cadastro)
def atualizar_cadastro(id_cadastro: int, cadastro: CadastroUpdate):
    existente = query("SELECT * FROM cadastro WHERE id_cadastro = ?", (id_cadastro,))
    if not existente:
        raise HTTPException(status_code=404, detail="Registro de cadastro não encontrado")

    if cadastro.status is not None:
        query("UPDATE cadastro SET status = ? WHERE id_cadastro = ?", (cadastro.status, id_cadastro))
    if cadastro.prioridade is not None:
        query("UPDATE cadastro SET prioridade = ? WHERE id_cadastro = ?", (cadastro.prioridade, id_cadastro))
    if cadastro.observacao is not None:
        query("UPDATE cadastro SET observacao = ? WHERE id_cadastro = ?", (cadastro.observacao, id_cadastro))
    if cadastro.responsavel is not None:
        query("UPDATE cadastro SET responsavel = ? WHERE id_cadastro = ?", (cadastro.responsavel, id_cadastro))

    return query("SELECT * FROM cadastro WHERE id_cadastro = ?", (id_cadastro,))[0]


@router.delete("/cadastro/{id_cadastro}")
def remover_cadastro(id_cadastro: int):
    existente = query("SELECT * FROM cadastro WHERE id_cadastro = ?", (id_cadastro,))
    if not existente:
        raise HTTPException(status_code=404, detail="Registro de cadastro não encontrado")

    query("DELETE FROM cadastro WHERE id_cadastro = ?", (id_cadastro,))
    return {"detail": "Registro removido"}