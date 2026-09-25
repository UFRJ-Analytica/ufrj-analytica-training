"""
Endpoints do trainee Miguel Marques.

Cobre as duas frentes pedidas na tarefa:
  1) Consulta e análise -> alimentam os gráficos do painel Streamlit.
  2) Município (dados básicos) + Cadastro (anotações do gestor) -> CRUD completo.

Convenção seguida (mesmo padrão usado por outros trainees, ex. Caroline Nomura):
  - todas as rotas ficam sob o prefixo /miguel-marques, para não colidir com
    as rotas de outros colegas que também usam FastAPI() ou APIRouter().
  - toda regra de negócio/agregação é feita em SQL, o Streamlit só exibe.
"""
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.database import query, execute

router = APIRouter(prefix="/miguel-marques", tags=["miguel_marques"])

# Constantes do domínio.
# A tabela populacao_municipal guarda um único indicador de interesse aqui, e
# mantemos esse filtro centralizado para evitar repetição em cada consulta.
INDICADOR_POPULACAO = "populacao_residente_estimada"
ANO_REFERENCIA = 2025

# Limites de porte do município (em habitantes), definidos por nós:
# pequeno < 20.000 | médio 20.000–100.000 | grande > 100.000.
PORTE_LIMITE_PEQUENO = 20_000
PORTE_LIMITE_MEDIO = 100_000

# Expressão SQL reutilizada em várias queries para classificar o porte.
SQL_PORTE_CASE = f"""
    CASE
        WHEN p.valor < {PORTE_LIMITE_PEQUENO} THEN 'Pequeno'
        WHEN p.valor < {PORTE_LIMITE_MEDIO} THEN 'Médio'
        ELSE 'Grande'
    END
"""


# Preparação do banco: criamos a tabela de cadastro e anotações do gestor na
# primeira importação deste módulo, porque essa informação não existe no banco
# original e foi pensada para uso interno do painel do Miguel.
def _garantir_tabela_acompanhamento() -> None:
    execute(
        """
        CREATE TABLE IF NOT EXISTS acompanhamento_municipal (
            id_acompanhamento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_municipio INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'monitorando',
            prioridade TEXT NOT NULL DEFAULT 'media',
            observacao TEXT,
            responsavel TEXT,
            atualizado_em TEXT NOT NULL,
            FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio)
        )
        """
    )


_garantir_tabela_acompanhamento()


# Schemas locais. Eles ficam neste módulo para evitar conflito com modelos de
# mesmo nome definidos em app/schemas.py por outros trainees.
class MunicipioMaisPopuloso(BaseModel):
    municipio: str
    uf: str
    populacao: int


class KPIs(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: int
    municipio_mais_populoso: Optional[MunicipioMaisPopuloso] = None


class MunicipioPopulacao(BaseModel):
    id_municipio: int
    nome_municipio: str
    uf: str
    populacao: int


class RegiaoPopulacao(BaseModel):
    id_regiao: int
    nome_regiao: str
    populacao_total: int


class EstadoPopulacao(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    nome_regiao: str
    populacao_total: int


class DispersaoEstado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    nome_regiao: str
    qtd_municipios: int
    populacao_media: float


class RegiaoPorte(BaseModel):
    nome_regiao: str
    porte: str
    quantidade: int


class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioUpdate(BaseModel):
    nome_municipio: Optional[str] = None
    id_uf: Optional[int] = None
    populacao: Optional[int] = None


class MunicipioOut(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int


class AcompanhamentoCreate(BaseModel):
    id_municipio: int
    status: Literal["monitorando", "alerta", "resolvido"] = "monitorando"
    prioridade: Literal["baixa", "media", "alta"] = "media"
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


class AcompanhamentoUpdate(BaseModel):
    status: Literal["monitorando", "alerta", "resolvido"]
    prioridade: Literal["baixa", "media", "alta"]
    observacao: Optional[str] = None
    responsavel: Optional[str] = None


class Acompanhamento(BaseModel):
    id_acompanhamento: int
    id_municipio: int
    nome_municipio: Optional[str] = None
    status: str
    prioridade: str
    observacao: Optional[str] = None
    responsavel: Optional[str] = None
    atualizado_em: str


# Helpers internos de validação para evitar repetição de SELECT e manter mensagens
# consistentes nas rotas do CRUD.
def _municipio_existe(id_municipio: int) -> bool:
    rows = query("SELECT 1 FROM municipios WHERE id_municipio = ?", (id_municipio,))
    return len(rows) > 0


def _uf_existe(id_uf: int) -> bool:
    rows = query("SELECT 1 FROM estados WHERE id_uf = ?", (id_uf,))
    return len(rows) > 0


def _populacao_atual(id_municipio: int) -> Optional[int]:
    rows = query(
        "SELECT valor FROM populacao_municipal WHERE id_municipio = ? AND indicador = ? AND ano = ?",
        (id_municipio, INDICADOR_POPULACAO, ANO_REFERENCIA),
    )
    return rows[0]["valor"] if rows else None


def _validar_municipio_payload(nome_municipio: Optional[str], id_uf: Optional[int], populacao: Optional[int]) -> None:
    if nome_municipio is not None and not nome_municipio.strip():
        raise HTTPException(status_code=400, detail="nome_municipio inválido.")
    if id_uf is not None and not _uf_existe(id_uf):
        raise HTTPException(status_code=400, detail="id_uf informado não existe.")
    if populacao is not None and populacao <= 0:
        raise HTTPException(status_code=400, detail="populacao deve ser maior que zero.")


def _validar_acompanhamento_payload(status: Optional[str], prioridade: Optional[str]) -> None:
    status_validos = {"monitorando", "alerta", "resolvido"}
    prioridade_validas = {"baixa", "media", "alta"}
    if status is not None and status not in status_validos:
        raise HTTPException(status_code=400, detail="status inválido.")
    if prioridade is not None and prioridade not in prioridade_validas:
        raise HTTPException(status_code=400, detail="prioridade inválida.")


# Consultas e análise para alimentar os gráficos do painel.
@router.get("/kpis", response_model=KPIs)
def kpis():
    """Números resumo para os KPIs do topo do painel."""
    total_municipios = query("SELECT COUNT(*) AS total FROM municipios")[0]["total"]
    total_estados = query("SELECT COUNT(*) AS total FROM estados")[0]["total"]

    populacao_total_rows = query(
        "SELECT SUM(valor) AS total FROM populacao_municipal WHERE indicador = ? AND ano = ?",
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )
    populacao_total = populacao_total_rows[0]["total"] or 0

    top1 = query(
        """
        SELECT m.nome_municipio AS municipio, e.sigla_uf AS uf, p.valor AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.indicador = ? AND p.ano = ?
        ORDER BY p.valor DESC
        LIMIT 1
        """,
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": ANO_REFERENCIA,
        "municipio_mais_populoso": top1[0] if top1 else None,
    }


@router.get("/municipios/top", response_model=list[MunicipioPopulacao])
def top_municipios(n: int = Query(default=10, ge=1, le=500)):
    """Ranking dos N municípios mais populosos (quantidade configurável)."""
    return query(
        """
        SELECT m.id_municipio AS id_municipio, m.nome_municipio AS nome_municipio,
               e.sigla_uf AS uf, p.valor AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.indicador = ? AND p.ano = ?
        ORDER BY p.valor DESC
        LIMIT ?
        """,
        (INDICADOR_POPULACAO, ANO_REFERENCIA, n),
    )


@router.get("/regioes", response_model=list[dict])
def listar_regioes_miguel():
    """Lista as regiões disponíveis para o filtro do Streamlit."""
    return query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")


@router.get("/regioes/populacao", response_model=list[RegiaoPopulacao])
def populacao_por_regiao():
    """População total agregada por região (para pizza/donut)."""
    return query(
        """
        SELECT r.id_regiao AS id_regiao,
               r.nome_regiao AS nome_regiao,
               COALESCE(SUM(p.valor), 0) AS populacao_total
        FROM regioes r
        LEFT JOIN estados e ON e.id_regiao = r.id_regiao
        LEFT JOIN municipios m ON m.id_uf = e.id_uf
        LEFT JOIN populacao_municipal p
            ON p.id_municipio = m.id_municipio
           AND p.indicador = ?
           AND p.ano = ?
        GROUP BY r.id_regiao, r.nome_regiao
        ORDER BY r.id_regiao
        """,
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )


@router.get("/estados/populacao", response_model=list[EstadoPopulacao])
def populacao_por_estado(id_regiao: Optional[int] = Query(default=None)):
    """População total por estado, com filtro opcional por região (para barras)."""
    sql = """
        SELECT e.id_uf AS id_uf, e.sigla_uf AS sigla_uf, e.nome_uf AS nome_uf,
               r.nome_regiao AS nome_regiao, SUM(p.valor) AS populacao_total
        FROM estados e
        JOIN regioes r ON r.id_regiao = e.id_regiao
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
            AND p.indicador = ? AND p.ano = ?
    """
    params: tuple = (INDICADOR_POPULACAO, ANO_REFERENCIA)
    if id_regiao is not None:
        sql += " WHERE e.id_regiao = ?"
        params += (id_regiao,)
    sql += " GROUP BY e.id_uf, e.sigla_uf, e.nome_uf, r.nome_regiao ORDER BY e.sigla_uf"
    return query(sql, params)


@router.get("/municipios/distribuicao", response_model=list[int])
def distribuicao_populacional():
    """População de todos os municípios, para montar o histograma no Streamlit."""
    rows = query(
        "SELECT valor FROM populacao_municipal WHERE indicador = ? AND ano = ?",
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )
    return [row["valor"] for row in rows]


@router.get("/estados/dispersao", response_model=list[DispersaoEstado])
def dispersao_por_estado():
    """Por estado: quantidade de municípios x população média (para scatter)."""
    return query(
        """
        SELECT e.id_uf AS id_uf, e.sigla_uf AS sigla_uf, e.nome_uf AS nome_uf,
               r.nome_regiao AS nome_regiao,
               COUNT(m.id_municipio) AS qtd_municipios,
               AVG(p.valor) AS populacao_media
        FROM estados e
        JOIN regioes r ON r.id_regiao = e.id_regiao
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
            AND p.indicador = ? AND p.ano = ?
        GROUP BY e.id_uf, e.sigla_uf, e.nome_uf, r.nome_regiao
        ORDER BY e.sigla_uf
        """,
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )


@router.get("/municipios/heatmap", response_model=list[RegiaoPorte])
def heatmap_regiao_porte():
    """Matriz região x porte (pequeno/médio/grande), para o mapa de calor."""
    resultado = query(
        f"""
        SELECT r.nome_regiao AS nome_regiao, {SQL_PORTE_CASE} AS porte,
               COUNT(*) AS quantidade
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.indicador = ? AND p.ano = ?
        GROUP BY r.nome_regiao, porte
        """,
        (INDICADOR_POPULACAO, ANO_REFERENCIA),
    )
    # Garante a matriz completa (região x porte), mesmo quando algum
    # cruzamento não tem nenhum município (fica 0 em vez de sumir do heatmap).
    regioes = [row["nome_regiao"] for row in query("SELECT nome_regiao FROM regioes ORDER BY id_regiao")]
    portes = ["Pequeno", "Médio", "Grande"]
    matriz = {(regiao, porte): 0 for regiao in regioes for porte in portes}
    for row in resultado:
        matriz[(row["nome_regiao"], row["porte"])] = row["quantidade"]
    return [
        {"nome_regiao": regiao, "porte": porte, "quantidade": quantidade}
        for (regiao, porte), quantidade in matriz.items()
    ]


# CRUD de município: dados básicos do cadastro e manutenção do registro.
@router.post("/municipios", response_model=MunicipioOut, status_code=201)
def criar_municipio(dados: MunicipioCreate):
    """Cadastra um município novo. Como não existe id oficial do IBGE para
    um município novo, geramos um: MAX(id_municipio) + 1."""
    _validar_municipio_payload(dados.nome_municipio, dados.id_uf, dados.populacao)

    max_id_row = query("SELECT MAX(id_municipio) AS max_id FROM municipios")[0]
    novo_id = (max_id_row["max_id"] or 0) + 1

    execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, dados.nome_municipio.strip(), dados.id_uf),
    )
    execute(
        """
        INSERT INTO populacao_municipal (id_municipio, ano, valor, indicador, unidade, fonte)
        VALUES (?, ?, ?, ?, 'pessoas', 'SISTEMA_GESTOR')
        """,
        (novo_id, ANO_REFERENCIA, dados.populacao, INDICADOR_POPULACAO),
    )

    return {
        "id_municipio": novo_id,
        "nome_municipio": dados.nome_municipio.strip(),
        "id_uf": dados.id_uf,
        "populacao": dados.populacao,
    }


@router.put("/municipios/{id_municipio}", response_model=MunicipioOut)
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    """Atualiza nome, estado e/ou população de um município existente.
    Apenas os campos enviados (não nulos) são alterados."""
    if not _municipio_existe(id_municipio):
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    _validar_municipio_payload(dados.nome_municipio, dados.id_uf, dados.populacao)

    atual = query(
        "SELECT nome_municipio, id_uf FROM municipios WHERE id_municipio = ?",
        (id_municipio,),
    )[0]
    novo_nome = dados.nome_municipio.strip() if dados.nome_municipio is not None else atual["nome_municipio"]
    novo_uf = dados.id_uf if dados.id_uf is not None else atual["id_uf"]

    execute(
        "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
        (novo_nome, novo_uf, id_municipio),
    )

    if dados.populacao is not None:
        execute(
            """
            UPDATE populacao_municipal SET valor = ?, fonte = 'SISTEMA_GESTOR'
            WHERE id_municipio = ? AND indicador = ? AND ano = ?
            """,
            (dados.populacao, id_municipio, INDICADOR_POPULACAO, ANO_REFERENCIA),
        )

    populacao_final = _populacao_atual(id_municipio) or 0
    return {
        "id_municipio": id_municipio,
        "nome_municipio": novo_nome,
        "id_uf": novo_uf,
        "populacao": populacao_final,
    }


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    """Remove um município e os dados dependentes dele (população e cadastro)."""
    if not _municipio_existe(id_municipio):
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    execute("DELETE FROM acompanhamento_municipal WHERE id_municipio = ?", (id_municipio,))
    execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
    execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))

    return {"detail": "Município removido com sucesso."}


# Cadastro do gestor: anotações complementares sobre os municípios.
@router.post("/acompanhamentos", response_model=Acompanhamento, status_code=201)
def criar_acompanhamento(dados: AcompanhamentoCreate):
    """Cria uma anotação do gestor (status, prioridade, observação, responsável)."""
    if not _municipio_existe(dados.id_municipio):
        raise HTTPException(status_code=400, detail="id_municipio informado não existe.")
    _validar_acompanhamento_payload(dados.status, dados.prioridade)

    agora = datetime.now().isoformat(timespec="seconds")
    execute(
        """
        INSERT INTO acompanhamento_municipal
            (id_municipio, status, prioridade, observacao, responsavel, atualizado_em)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (dados.id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel, agora),
    )
    novo_id = query("SELECT MAX(id_acompanhamento) AS max_id FROM acompanhamento_municipal")[0]["max_id"]
    return _buscar_acompanhamento_ou_404(novo_id)


@router.get("/acompanhamentos", response_model=list[Acompanhamento])
def listar_acompanhamentos(id_municipio: Optional[int] = Query(default=None)):
    """Lista as anotações do gestor, com filtro opcional por município."""
    sql = """
        SELECT a.id_acompanhamento AS id_acompanhamento, a.id_municipio AS id_municipio,
               m.nome_municipio AS nome_municipio, a.status AS status,
               a.prioridade AS prioridade, a.observacao AS observacao,
               a.responsavel AS responsavel, a.atualizado_em AS atualizado_em
        FROM acompanhamento_municipal a
        JOIN municipios m ON m.id_municipio = a.id_municipio
    """
    params: tuple = ()
    if id_municipio is not None:
        sql += " WHERE a.id_municipio = ?"
        params = (id_municipio,)
    sql += " ORDER BY a.atualizado_em DESC"
    return query(sql, params)


@router.put("/acompanhamentos/{id_acompanhamento}", response_model=Acompanhamento)
def atualizar_acompanhamento(id_acompanhamento: int, dados: AcompanhamentoUpdate):
    """Atualiza uma anotação existente do gestor."""
    _buscar_acompanhamento_ou_404(id_acompanhamento)
    _validar_acompanhamento_payload(dados.status, dados.prioridade)
    agora = datetime.now().isoformat(timespec="seconds")
    execute(
        """
        UPDATE acompanhamento_municipal
        SET status = ?, prioridade = ?, observacao = ?, responsavel = ?, atualizado_em = ?
        WHERE id_acompanhamento = ?
        """,
        (dados.status, dados.prioridade, dados.observacao, dados.responsavel, agora, id_acompanhamento),
    )
    return _buscar_acompanhamento_ou_404(id_acompanhamento)


@router.delete("/acompanhamentos/{id_acompanhamento}")
def remover_acompanhamento(id_acompanhamento: int):
    """Remove uma anotação do gestor."""
    _buscar_acompanhamento_ou_404(id_acompanhamento)
    execute("DELETE FROM acompanhamento_municipal WHERE id_acompanhamento = ?", (id_acompanhamento,))
    return {"detail": "Anotação removida com sucesso."}


def _buscar_acompanhamento_ou_404(id_acompanhamento: int) -> dict:
    """Helper: busca uma anotação pelo id ou lança 404. Reaproveitado por
    criar/atualizar (para devolver o registro completo já com o nome do
    município) e por atualizar/remover (para validar existência)."""
    rows = query(
        """
        SELECT a.id_acompanhamento AS id_acompanhamento, a.id_municipio AS id_municipio,
               m.nome_municipio AS nome_municipio, a.status AS status,
               a.prioridade AS prioridade, a.observacao AS observacao,
               a.responsavel AS responsavel, a.atualizado_em AS atualizado_em
        FROM acompanhamento_municipal a
        JOIN municipios m ON m.id_municipio = a.id_municipio
        WHERE a.id_acompanhamento = ?
        """,
        (id_acompanhamento,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Anotação não encontrada.")
    return rows[0]