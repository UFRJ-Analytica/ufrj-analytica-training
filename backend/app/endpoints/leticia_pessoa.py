from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.database import query, get_connection
from app.schemas import KpiResponse, TopMunicipio, PopulacaoPorRegiao, PopulacaoPorEstado, DispersaoMunicipioEstado, RegiaoPorte, MunicipioCreate, MunicipioResponse, MunicipioUpdate, CadastroCreate, CadastroUpdate, CadastroResponse

router = APIRouter(prefix="/leticia-pessoa", tags=["leticia-pessoa"])

# ---------------------------------------------------------------------------
# 1. Funções auxiliares locais
# ---------------------------------------------------------------------------
def execute(sql: str, params: tuple = ())-> int:
    """Executa INSERT, UPDATE ou DELETE(função local, só desse arquivo)."""
    conn = get_connection()
    try:
        cursor = conn. execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def municipio_existe(id_municipio: int) -> bool:
    """Verifica se um município com esse id existe no banco."""
    resultado = query(
        "SELECT id_municipio FROM municipios WHERE id_municipio = ?",
        (id_municipio,)
    )
    return len(resultado) > 0

def estado_existe(id_uf: int) -> bool:
    resultado = query("SELECT id_uf FROM estados WHERE id_uf = ?", (id_uf,))
    return len(resultado) > 0

def ano_referencia() -> int:
    """Devolve o ano mais recente disponível na tabela de população."""
    return query("SELECT MAX(ano) AS ano FROM populacao")[0]["ano"]

# ---------------------------------------------------------------------------
# 2. Análise
# ---------------------------------------------------------------------------
@router.get("/status")
def status():
    return{"status": "ok"}

@router.get("/estatisticas/resumo", response_model=KpiResponse)
def kpis():

    ano = ano_referencia()

    total_municipios = query ("SELECT COUNT(*) AS total FROM municipios")[0]["total"]
    total_estados = query ("SELECT COUNT(*) AS total FROM estados")[0]["total"]

    populacao_total = query("SELECT SUM(valor_populacao) AS total FROM populacao WHERE ano =?",(ano,))[0]["total"]

    municipio_mais_populoso = query(
        """
        SELECT 
            m.nome_municipio AS nome
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        WHERE p.ano = ?
        ORDER BY p.valor_populacao DESC
        LIMIT 1
        """,
        (ano,)
    )[0]["nome"]

    return KpiResponse(
        total_municipios=total_municipios,
        total_estados=total_estados,
        populacao_total=populacao_total,
        ano_referencia=ano,
        municipio_mais_populoso=municipio_mais_populoso,
    )

@router.get("/populacao/top_municipios", response_model = list[TopMunicipio])
def top_municipios(n: int):
    return query(
        """
        SELECT 
            m.nome_municipio AS nome,
            p.valor_populacao AS populacao
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        WHERE p.ano = (SELECT MAX(ano) FROM populacao)
        ORDER BY p.valor_populacao DESC
        LIMIT ?
        """,
        (n,)
    )

@router.get("/populacao/por-regiao", response_model= list[PopulacaoPorRegiao])
def populacao_regiao():
    return query(
        """
        SELECT 
            r.nome_regiao AS regiao, SUM(valor_populacao) AS populacao
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano = (SELECT MAX(ano) FROM populacao)
        GROUP BY r.nome_regiao
        ORDER BY populacao DESC
        """
    )

@router.get("/populacao/por-uf", response_model=list[PopulacaoPorEstado])
def populacao_por_estado(regiao: str | None = Query(default=None)):
    return query(
        """
        SELECT
            r.nome_regiao AS regiao,
            e.nome_uf AS estado,
            SUM(valor_populacao) AS populacao
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano = (SELECT MAX(ano) FROM populacao)
            AND (? IS NULL OR r.nome_regiao = ?)
        GROUP BY estado
        ORDER BY populacao DESC
        """,
        (regiao, regiao)
    )

@router.get("/populacao/municipio")
def populacao_por_municipio():
    return query(
        """
        SELECT
            m.nome_municipio,
            p.valor_populacao AS populacao
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        WHERE p.ano = (SELECT MAX(ano) FROM populacao)
        ORDER BY populacao DESC
        """
    )

@router.get("/populacao/dispersao-uf", response_model=list[DispersaoMunicipioEstado])
def dispersao_municipio_estado():
    return query(
        """
        SELECT
            e.nome_uf AS estado,
            r.nome_regiao AS regiao,
            COUNT(m.id_municipio) AS quantidade_municipios,
            AVG(p.valor_populacao) AS populacao_media
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano=(SELECT MAX(ano) FROM populacao)
        GROUP BY e.nome_uf, r.nome_regiao
        ORDER BY e.nome_uf
        """
    )

@router.get("/populacao/heatmap-regiao-porte", response_model=list[RegiaoPorte])
def heatmap():
    return query(
        """
        SELECT 
            r.nome_regiao AS regiao ,
            CASE
                WHEN p.valor_populacao <= 20000 THEN 'Pequeno'
                WHEN p.valor_populacao <= 100000 THEN 'Medio'
                ELSE 'Grande'
            END AS porte,
            COUNT(*) AS quantidade
        FROM populacao p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano=(SELECT MAX(ano) FROM populacao)
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao, porte
        """
    )

# ---------------------------------------------------------------------------
# 3. Municipios
# ---------------------------------------------------------------------------

# Endpoints
@router.post("/municipios", response_model=MunicipioResponse)
def criar_municipio(municipio: MunicipioCreate):
    if not estado_existe( municipio.id_uf):
        raise HTTPException(status_code=404, detail="id_uf informado não existe")
    maior_id = query("SELECT MAX(id_municipio) AS maior FROM municipios")[0]["maior"]
    novo_id = (maior_id or 0) + 1

    execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, municipio.nome_municipio, municipio.id_uf)
    )

    execute(
        "INSERT INTO populacao (id_municipio, ano, valor_populacao) VALUES (?, ?, ?)",
        (novo_id, ano_referencia(), municipio.populacao)
    )
    return MunicipioResponse(
        id_municipio=novo_id,
        nome_municipio=municipio.nome_municipio,
        id_uf = municipio.id_uf,
        populacao = municipio.populacao,
    )

@router.get("/municipios", response_model=list[MunicipioResponse])
def listar_municipios():
    return query(
        """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            m.id_uf,
            COALESCE(p.valor_populacao, 0) AS populacao
        FROM municipios m
        LEFT JOIN populacao p ON p.id_municipio = m.id_municipio
            AND p.ano = (SELECT MAX(ano) FROM populacao)
        """
    )


@router.get("/municipios/{id_municipio}", response_model=MunicipioResponse)
def buscar_municipio(id_municipio: int):
    resultado = query(
        """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            m.id_uf,
            COALESCE(p.valor_populacao, 0) AS populacao
        FROM municipios m
        LEFT JOIN populacao p ON p.id_municipio = m.id_municipio
            AND p.ano = (SELECT MAX(ano) FROM populacao)
        WHERE m.id_municipio = ?
        """,
        (id_municipio,)
    )
    if not resultado:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return resultado[0]

@router.put("/municipios/{id_municipio}", response_model=MunicipioResponse)
def atualizar_municipio(id_municipio: int, municipio: MunicipioUpdate):
    if not municipio_existe(id_municipio):
        raise HTTPException(status=404, detail="Município não encontrado")

    dados_atuais = buscar_municipio(id_municipio)

    # Atualizar municipio
    novo_nome = municipio.nome_municipio if municipio.nome_municipio is not None else dados_atuais["nome_municipio"]
    novo_uf = municipio.id_uf if municipio.id_uf is not None else dados_atuais["id_uf"]
    nova_populacao = municipio.populacao if municipio.populacao is not None else dados_atuais["populacao"]

    if municipio.id_uf is not None and not estado_existe(municipio.id_uf):
        raise HTTPException(status_code=400, detail="id_uf informado não existe")

    execute(
        "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
        (novo_nome, novo_uf, id_municipio)
    )

    # Atualizar populacao
    existe_pop = query("SELECT 1 FROM populacao WHERE id_municipio = ? AND ano = ?",(id_municipio, ano_referencia()))

    if existe_pop:
        execute(
            "UPDATE populacao SET valor_populacao = ? WHERE id_municipio = ? AND ano = ?",
            (nova_populacao, id_municipio, ano_referencia())
        )
    else:
        execute(
            "INSERT INTO populacao(id_municipio, ano, valor_populacao) VALUES (?,?,?)",
            (id_municipio, ano_referencia(), nova_populacao)
        )
    return buscar_municipio(id_municipio)

@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    if not municipio_existe(id_municipio):
        raise HTTPException(status_code=404, detail="Município não encontrado")

    # Limpeza de dependencias
    execute("DELETE FROM populacao WHERE id_municipio = ?", (id_municipio,))
    execute("DELETE FROM cadastro_municipio WHERE id_municipio = ?", (id_municipio,))
    execute("DELETE FROM municipios WHERE id_municipio =?", (id_municipio,))

    return {"mensagem": "Município removido com sucesso"}

# ---------------------------------------------------------------------------
# 4. Cadastro: informações de gestão
# ---------------------------------------------------------------------------

@router.post("/cadastro", response_model=CadastroResponse)
def criar_cadastro(cadastro: CadastroCreate):
    if not municipio_existe(cadastro.id_municipio):
        raise HTTPException(status=404,detail="Município não encontrado")

    agora = datetime.now().isoformat()

    novo_id = execute(
        """
        INSERT INTO cadastro_municipio
            (id_municipio, status, prioridade, observacao, responsavel, data_criacao)    
        VALUES(?,?,?,?,?,?)
        """,
        (cadastro.id_municipio, cadastro.status, cadastro.prioridade, cadastro.observacao, cadastro.responsavel, agora)
    )

    return buscar_cadastro(novo_id)


@router.get("/cadastro", response_model=list[CadastroResponse])
def listar_cadastro():
    return query("SELECT * FROM cadastro_municipio")


@router.get("/cadastro/{id_cadastro}",response_model=CadastroResponse)
def buscar_cadastro(id_cadastro:int):
    resultado = query(
        "SELECT * FROM cadastro_municipio WHERE id_cadastro = ?",
        (id_cadastro,)
    )
    if not resultado:
        raise HTTPException(status_code=404, detail="Cadastro não encontrado")
    return resultado[0]


@router.put("/cadastro/{id_cadastro}", response_model=CadastroResponse)
def atualizar_cadastro(id_cadastro: int, cadastro: CadastroUpdate):
    existente = query("SELECT * FROM cadastro_municipio WHERE id_cadastro = ?",(id_cadastro,))
    if not existente:
        raise HTTPException(status_code=404, detail="Cadastro não encontrado")

    atual = existente[0]
    novo_status = cadastro.status if cadastro.status is not None else atual["status"]
    novo_prioridade = cadastro.prioridade if cadastro.prioridade is not None else atual["prioridade"]
    novo_observacao = cadastro.observacao if cadastro.observacao is not None else atual["observacao"]
    novo_responsavel = cadastro.responsavel if cadastro.responsavel is not None else atual["responsavel"]

    execute(
        """
        UPDATE cadastro_municipio
        SET status = ?, prioridade =?, observacao =?, responsavel=?
        WHERE id_cadastro =?
        """,
        (novo_status, novo_prioridade, novo_observacao, novo_responsavel, id_cadastro)
    )

    return buscar_cadastro(id_cadastro)

@router.delete("/cadastro/{id_cadastro}")
def remover_cadastro(id_cadastro:int):
    existente = query("SELECT * FROM cadastro_municipio WHERE id_cadastro = ?", (id_cadastro,))
    if not existente:
        raise HTTPException(status_code=404, detail="Cadastro não encontrado")

    execute("DELETE FROM cadastro_municipio WHERE id_cadastro = ?", (id_cadastro,))
    return{"mensagem": "Cadastro removido com sucesso"}
    