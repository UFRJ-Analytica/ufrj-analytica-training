"""
Endpoints de Isaac Vianna: sistema de acompanhamento populacional.

Duas frentes, como pedido no tarefa.md:
- Análise: KPIs e agregações (região, estado, distribuição, dispersão, heatmap).
- Cadastro: CRUD de município (dados do IBGE) e CRUD de "cadastro" (anotação
  do gestor, tabela nova que não existia no database.db original).

Tudo fica isolado aqui (router com prefixo próprio, modelos Pydantic locais)
pra não esbarrar no trabalho de outros trainees.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.database import get_connection, query

router = APIRouter(prefix="/isaac-vianna", tags=["isaac_vianna"])

# Limites de população usados para classificar o "porte" de um município no
# heatmap. Não existe um corte oficial do IBGE pra isso, então definimos um
# que faz sentido olhando a distribuição real dos dados (a maioria dos
# municípios brasileiros é pequena).
LIMITE_PEQUENO = 20_000
LIMITE_MEDIO = 100_000


def _execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. query() do database.py só cobre SELECT.

    Retorna o lastrowid da própria conexão (last_insert_rowid() é por conexão,
    então precisa ser lido aqui, não numa query() separada depois).
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def _criar_tabela_cadastro() -> None:
    _execute(
        """
        CREATE TABLE IF NOT EXISTS cadastro_municipios (
            id_registro   INTEGER PRIMARY KEY AUTOINCREMENT,
            id_municipio  INTEGER NOT NULL REFERENCES municipios(id_municipio),
            status        TEXT NOT NULL,
            prioridade    TEXT NOT NULL,
            observacao    TEXT,
            responsavel   TEXT,
            criado_em     TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        )
        """
    )


_criar_tabela_cadastro()


# ---------------------------------------------------------------------------
# Modelos Pydantic
# ---------------------------------------------------------------------------

class ResumoEstatisticas(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total: int
    ano_referencia: int
    municipio_mais_populoso: str
    sigla_uf_mais_populoso: str
    populacao_mais_populoso: int


class TopMunicipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    sigla_uf: str
    populacao: int


class PopulacaoRegiao(BaseModel):
    id_regiao: int
    sigla_regiao: str
    nome_regiao: str
    populacao_total: int


class PopulacaoUF(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int
    populacao_total: int


class MunicipioPopulacao(BaseModel):
    id_municipio: int
    nome_municipio: str
    sigla_uf: str
    populacao: int


class DispersaoUF(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int
    sigla_regiao: str
    quantidade_municipios: int
    populacao_media: float


class HeatmapCelula(BaseModel):
    sigla_regiao: str
    porte: str
    quantidade: int


class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str
    id_regiao: int


class Municipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int | None = None


class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    populacao: int


class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    populacao: int | None = None


class CadastroMunicipio(BaseModel):
    id_registro: int
    id_municipio: int
    status: str
    prioridade: str
    observacao: str | None
    responsavel: str | None
    criado_em: str
    atualizado_em: str


class CadastroCreate(BaseModel):
    status: str
    prioridade: str
    observacao: str | None = None
    responsavel: str | None = None


class CadastroUpdate(BaseModel):
    status: str | None = None
    prioridade: str | None = None
    observacao: str | None = None
    responsavel: str | None = None


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _buscar_municipio(id_municipio: int) -> dict | None:
    rows = query(
        """
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, pm.valor AS populacao
        FROM municipios m
        LEFT JOIN populacao_municipal pm ON pm.id_municipio = m.id_municipio
        WHERE m.id_municipio = ?
        """,
        (id_municipio,),
    )
    return rows[0] if rows else None


def _ano_referencia() -> int:
    rows = query("SELECT MAX(ano) AS ano FROM populacao_municipal")
    return rows[0]["ano"]


def _classificar_porte(populacao: int) -> str:
    if populacao < LIMITE_PEQUENO:
        return "pequeno"
    if populacao < LIMITE_MEDIO:
        return "medio"
    return "grande"


# ---------------------------------------------------------------------------
# Análise
# ---------------------------------------------------------------------------

@router.get("/estatisticas/resumo", response_model=ResumoEstatisticas)
def resumo_estatistico():
    total_municipios = query("SELECT COUNT(*) AS n FROM municipios")[0]["n"]
    total_estados = query("SELECT COUNT(*) AS n FROM estados")[0]["n"]
    populacao_total = query("SELECT SUM(valor) AS soma FROM populacao_municipal")[0]["soma"]
    ano_referencia = _ano_referencia()

    mais_populoso = query(
        """
        SELECT m.nome_municipio, e.sigla_uf, pm.valor AS populacao
        FROM populacao_municipal pm
        JOIN municipios m ON m.id_municipio = pm.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        ORDER BY pm.valor DESC
        LIMIT 1
        """
    )[0]

    return ResumoEstatisticas(
        total_municipios=total_municipios,
        total_estados=total_estados,
        populacao_total=populacao_total,
        ano_referencia=ano_referencia,
        municipio_mais_populoso=mais_populoso["nome_municipio"],
        sigla_uf_mais_populoso=mais_populoso["sigla_uf"],
        populacao_mais_populoso=mais_populoso["populacao"],
    )


@router.get("/populacao/top-municipios", response_model=list[TopMunicipio])
def top_municipios(limit: int = Query(default=10, le=100)):
    rows = query(
        """
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, pm.valor AS populacao
        FROM populacao_municipal pm
        JOIN municipios m ON m.id_municipio = pm.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        ORDER BY pm.valor DESC
        LIMIT ?
        """,
        (limit,),
    )
    return rows


@router.get("/populacao/por-regiao", response_model=list[PopulacaoRegiao])
def populacao_por_regiao():
    rows = query(
        """
        SELECT r.id_regiao, r.sigla_regiao, r.nome_regiao, SUM(pm.valor) AS populacao_total
        FROM regioes r
        JOIN estados e ON e.id_regiao = r.id_regiao
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN populacao_municipal pm ON pm.id_municipio = m.id_municipio
        GROUP BY r.id_regiao
        ORDER BY r.id_regiao
        """
    )
    return rows


@router.get("/populacao/por-uf", response_model=list[PopulacaoUF])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT e.id_uf, e.sigla_uf, e.nome_uf, e.id_regiao, SUM(pm.valor) AS populacao_total
        FROM estados e
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN populacao_municipal pm ON pm.id_municipio = m.id_municipio
    """
    params: tuple = ()
    if id_regiao is not None:
        sql += " WHERE e.id_regiao = ?"
        params = (id_regiao,)
    sql += " GROUP BY e.id_uf ORDER BY e.sigla_uf"

    return query(sql, params)


@router.get("/populacao/distribuicao", response_model=list[MunicipioPopulacao])
def distribuicao_populacional():
    rows = query(
        """
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, pm.valor AS populacao
        FROM populacao_municipal pm
        JOIN municipios m ON m.id_municipio = pm.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        """
    )
    return rows


@router.get("/populacao/dispersao-uf", response_model=list[DispersaoUF])
def dispersao_por_uf():
    rows = query(
        """
        SELECT
            e.id_uf, e.sigla_uf, e.nome_uf, e.id_regiao, r.sigla_regiao,
            COUNT(m.id_municipio) AS quantidade_municipios,
            AVG(pm.valor) AS populacao_media
        FROM estados e
        JOIN regioes r ON r.id_regiao = e.id_regiao
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN populacao_municipal pm ON pm.id_municipio = m.id_municipio
        GROUP BY e.id_uf
        ORDER BY e.sigla_uf
        """
    )
    return rows


@router.get("/populacao/heatmap-regiao-porte", response_model=list[HeatmapCelula])
def heatmap_regiao_porte():
    rows = query(
        """
        SELECT r.sigla_regiao, pm.valor AS populacao
        FROM populacao_municipal pm
        JOIN municipios m ON m.id_municipio = pm.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        """
    )

    regioes = query("SELECT sigla_regiao FROM regioes ORDER BY id_regiao")
    portes = ["pequeno", "medio", "grande"]

    # Inicializa a matriz toda com zero, senão combinações sem município
    # nenhum ficariam faltando no heatmap.
    contagem = {r["sigla_regiao"]: {p: 0 for p in portes} for r in regioes}

    for row in rows:
        porte = _classificar_porte(row["populacao"])
        contagem[row["sigla_regiao"]][porte] += 1

    return [
        HeatmapCelula(sigla_regiao=sigla, porte=porte, quantidade=quantidade)
        for sigla, portes_contagem in contagem.items()
        for porte, quantidade in portes_contagem.items()
    ]


@router.get("/estados", response_model=list[Estado])
def listar_estados(id_regiao: int | None = Query(default=None)):
    sql = "SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados"
    params: tuple = ()
    if id_regiao is not None:
        sql += " WHERE id_regiao = ?"
        params = (id_regiao,)
    sql += " ORDER BY sigla_uf"
    return query(sql, params)


# ---------------------------------------------------------------------------
# Município (dados básicos) — CRUD
# ---------------------------------------------------------------------------

@router.get("/municipios", response_model=list[Municipio])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    sql = """
        SELECT m.id_municipio, m.nome_municipio, m.id_uf, pm.valor AS populacao
        FROM municipios m
        LEFT JOIN populacao_municipal pm ON pm.id_municipio = m.id_municipio
        WHERE 1=1
    """
    params: list = []
    if nome is not None:
        sql += " AND m.nome_municipio LIKE ?"
        params.append(f"%{nome}%")
    if id_uf is not None:
        sql += " AND m.id_uf = ?"
        params.append(id_uf)
    sql += " ORDER BY m.nome_municipio LIMIT ?"
    params.append(limit)

    return query(sql, tuple(params))


@router.get("/municipios/{id_municipio}", response_model=Municipio)
def detalhe_municipio(id_municipio: int):
    municipio = _buscar_municipio(id_municipio)
    if municipio is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return municipio


@router.post("/municipios", response_model=Municipio, status_code=201)
def criar_municipio(dados: MunicipioCreate):
    estado = query("SELECT id_uf FROM estados WHERE id_uf = ?", (dados.id_uf,))
    if not estado:
        raise HTTPException(status_code=400, detail="Estado (id_uf) inválido")

    novo_id = query("SELECT MAX(id_municipio) AS max_id FROM municipios")[0]["max_id"] + 1
    ano = _ano_referencia()

    _execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, dados.nome_municipio, dados.id_uf),
    )
    _execute(
        "INSERT INTO populacao_municipal (id_municipio, ano, valor) VALUES (?, ?, ?)",
        (novo_id, ano, dados.populacao),
    )

    return _buscar_municipio(novo_id)


@router.put("/municipios/{id_municipio}", response_model=Municipio)
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    municipio = _buscar_municipio(id_municipio)
    if municipio is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    if dados.id_uf is not None:
        estado = query("SELECT id_uf FROM estados WHERE id_uf = ?", (dados.id_uf,))
        if not estado:
            raise HTTPException(status_code=400, detail="Estado (id_uf) inválido")

    if dados.nome_municipio is not None or dados.id_uf is not None:
        novo_nome = dados.nome_municipio if dados.nome_municipio is not None else municipio["nome_municipio"]
        novo_uf = dados.id_uf if dados.id_uf is not None else municipio["id_uf"]
        _execute(
            "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
            (novo_nome, novo_uf, id_municipio),
        )

    if dados.populacao is not None:
        ano = _ano_referencia()
        _execute(
            "INSERT OR REPLACE INTO populacao_municipal (id_municipio, ano, valor) VALUES (?, ?, ?)",
            (id_municipio, ano, dados.populacao),
        )

    return _buscar_municipio(id_municipio)


@router.delete("/municipios/{id_municipio}", status_code=204)
def remover_municipio(id_municipio: int):
    municipio = _buscar_municipio(id_municipio)
    if municipio is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    _execute("DELETE FROM cadastro_municipios WHERE id_municipio = ?", (id_municipio,))
    _execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
    _execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))


# ---------------------------------------------------------------------------
# Cadastro (anotação do gestor) — CRUD
# ---------------------------------------------------------------------------

@router.post(
    "/municipios/{id_municipio}/registros",
    response_model=CadastroMunicipio,
    status_code=201,
)
def criar_registro(id_municipio: int, dados: CadastroCreate):
    if _buscar_municipio(id_municipio) is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    agora = datetime.now().isoformat(timespec="seconds")
    novo_id = _execute(
        """
        INSERT INTO cadastro_municipios
            (id_municipio, status, prioridade, observacao, responsavel, criado_em, atualizado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel, agora, agora),
    )

    return query("SELECT * FROM cadastro_municipios WHERE id_registro = ?", (novo_id,))[0]


@router.get("/municipios/{id_municipio}/registros", response_model=list[CadastroMunicipio])
def listar_registros(id_municipio: int):
    if _buscar_municipio(id_municipio) is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return query(
        "SELECT * FROM cadastro_municipios WHERE id_municipio = ? ORDER BY criado_em DESC",
        (id_municipio,),
    )


@router.put("/registros/{id_registro}", response_model=CadastroMunicipio)
def atualizar_registro(id_registro: int, dados: CadastroUpdate):
    registro = query("SELECT * FROM cadastro_municipios WHERE id_registro = ?", (id_registro,))
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    registro = registro[0]

    novo_status = dados.status if dados.status is not None else registro["status"]
    nova_prioridade = dados.prioridade if dados.prioridade is not None else registro["prioridade"]
    nova_observacao = dados.observacao if dados.observacao is not None else registro["observacao"]
    novo_responsavel = dados.responsavel if dados.responsavel is not None else registro["responsavel"]
    agora = datetime.now().isoformat(timespec="seconds")

    _execute(
        """
        UPDATE cadastro_municipios
        SET status = ?, prioridade = ?, observacao = ?, responsavel = ?, atualizado_em = ?
        WHERE id_registro = ?
        """,
        (novo_status, nova_prioridade, nova_observacao, novo_responsavel, agora, id_registro),
    )

    return query("SELECT * FROM cadastro_municipios WHERE id_registro = ?", (id_registro,))[0]


@router.delete("/registros/{id_registro}", status_code=204)
def remover_registro(id_registro: int):
    registro = query("SELECT * FROM cadastro_municipios WHERE id_registro = ?", (id_registro,))
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    _execute("DELETE FROM cadastro_municipios WHERE id_registro = ?", (id_registro,))
