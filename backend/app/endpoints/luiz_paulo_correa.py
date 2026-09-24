from fastapi import APIRouter, HTTPException, Query
from app.schemas import (
    Municipio,
    Estado,
    Regiao,
    ResumoEstatistico,
    MunicipioPopulacao,
    PopulacaoPorRegiao,
    PopulacaoPorEstado,
    DispersaoEstado,
    HeatmapRegiaoPorte,
    MunicipioCreate,
    MunicipioUpdate,
    MunicipioComPopulacao,
    RegistroGestorCreate,
    RegistroGestorUpdate,
    RegistroGestor,
)

from app.database import query, get_connection

router = APIRouter(prefix="/luiz-paulo", tags=["luiz_paulo"])

# Rota de teste
@router.get("/status")
def status():
    return {"status": "ok", "mensagem": "funcionando"}

@router.get("/estados", response_model=list[Estado])
def listar_estados():
    return query("SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados")

@router.get("/regioes", response_model=list[Regiao])
def listar_regioes():
    return query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes")

@router.get("/municipios", response_model=list[Municipio])
def listar_municipios():
    return query("SELECT id_municipio, nome_municipio, id_uf FROM municipios")

@router.get("/municipios/{id_municipio}", response_model=Municipio)
def buscar_municipio(id_municipio: int):
    rows = query(
        "SELECT id_municipio, nome_municipio, id_uf FROM municipios WHERE id_municipio = ?",
        (id_municipio,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return rows[0]

#paineis de análise para streamlit

@router.get("/estatisticas/resumo", response_model=ResumoEstatistico) #KPIs
def resumo_estatistico():
    total_municipios = query("SELECT COUNT(*) AS total FROM municipios")[0]["total"]
    total_estados = query("SELECT COUNT(*) AS total FROM estados")[0]["total"]
    ano_referencia = query("SELECT MAX(ano) AS ano FROM populacao_municipal")[0]["ano"]
    populacao_total = query(
        "SELECT SUM(valor) AS total FROM populacao_municipal WHERE ano = ?",
        (ano_referencia,),
    )[0]["total"]
    mais_populoso = query(
        """
        SELECT m.nome_municipio, e.sigla_uf, p.valor
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = ?
        ORDER BY p.valor DESC
        LIMIT 1
        """,
        (ano_referencia,),
    )[0]

    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": ano_referencia,
        "municipio_mais_populoso": mais_populoso["nome_municipio"],
        "uf_municipio_mais_populoso": mais_populoso["sigla_uf"],
        "populacao_municipio_mais_populoso": mais_populoso["valor"],
    }


@router.get("/populacao/top-municipios", response_model=list[MunicipioPopulacao]) #topN
def top_municipios(limit: int = Query(default=10, le=100)):
    return query(
        """
        SELECT m.nome_municipio, e.sigla_uf, p.valor
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        ORDER BY p.valor DESC
        LIMIT ?
        """,
        (limit,),
    )


@router.get("/populacao/por-regiao", response_model=list[PopulacaoPorRegiao]) #pop. regiao
def populacao_por_regiao():
    return query(
        """
        SELECT r.nome_regiao, SUM(p.valor) AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        GROUP BY r.nome_regiao
        ORDER BY populacao DESC
        """
    )


@router.get("/populacao/por-uf", response_model=list[PopulacaoPorEstado]) #pop. estado
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT e.nome_uf, e.sigla_uf, SUM(p.valor) AS populacao
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
    """
    params: tuple = ()
    if id_regiao is not None:
        sql += " AND e.id_regiao = ?"
        params = (id_regiao,)
    sql += " GROUP BY e.nome_uf, e.sigla_uf ORDER BY populacao DESC"
    return query(sql, params)


@router.get("/populacao/distribuicao", response_model=list[MunicipioPopulacao]) #distr. pop.
def distribuicao_populacional():
    return query(
        """
        SELECT m.nome_municipio, e.sigla_uf, p.valor
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        """
    )


@router.get("/populacao/dispersao-uf", response_model=list[DispersaoEstado])
def dispersao_por_uf():
    return query(
        """
        SELECT e.nome_uf, e.sigla_uf, r.nome_regiao,
               COUNT(m.id_municipio) AS qtd_municipios,
               AVG(p.valor) AS populacao_media
        FROM municipios m
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        GROUP BY e.nome_uf, e.sigla_uf, r.nome_regiao
        ORDER BY qtd_municipios DESC
        """
    )


@router.get("/populacao/heatmap-regiao-porte", response_model=list[HeatmapRegiaoPorte])
def heatmap_regiao_porte():
    return query(
        """
        SELECT r.nome_regiao,
               CASE
                   WHEN p.valor <= 20000 THEN 'Pequeno'
                   WHEN p.valor BETWEEN 20001 AND 100000 THEN 'Médio'
                   ELSE 'Grande'
               END AS porte,
               COUNT(*) AS quantidade
        FROM populacao_municipal p
        JOIN municipios m ON m.id_municipio = p.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        WHERE p.ano = (SELECT MAX(ano) FROM populacao_municipal)
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao, porte
        """
    )

#CRUD de município 

def _execute(sql: str, params: tuple = ()) -> int:
    """executa um INSERT/UPDATE/DELETE com FK. comita, e devolve
    cursor.lastrowid."""
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def _ano_referencia() -> int:
    return query("SELECT MAX(ano) AS ano FROM populacao_municipal")[0]["ano"]


def _buscar_municipio_com_populacao(id_municipio: int) -> dict | None:
    rows = query(
        """
        SELECT m.id_municipio, m.nome_municipio, m.id_uf,
               COALESCE(p.valor, 0) AS populacao
        FROM municipios m
        LEFT JOIN populacao_municipal p
            ON p.id_municipio = m.id_municipio AND p.ano = ?
        WHERE m.id_municipio = ?
        """,
        (_ano_referencia(), id_municipio),
    )
    return rows[0] if rows else None


@router.post("/municipios", response_model=MunicipioComPopulacao, status_code=201)
def criar_municipio(dados: MunicipioCreate):
    if not query("SELECT id_uf FROM estados WHERE id_uf = ?", (dados.id_uf,)): # testa se o estado existe
        raise HTTPException(status_code=404, detail="Estado (id_uf) não encontrado")

    novo_id = query("SELECT MAX(id_municipio) AS max_id FROM municipios")[0]["max_id"] + 1
    ano = _ano_referencia()

    _execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, dados.nome_municipio, dados.id_uf),
    )
    _execute(
        """
        INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
        VALUES (?, ?, 'populacao_residente_estimada', ?, 'pessoas', 'cadastro manual')
        """,
        (novo_id, ano, dados.populacao),
    )
    return _buscar_municipio_com_populacao(novo_id)


@router.put("/municipios/{id_municipio}", response_model=MunicipioComPopulacao)
def atualizar_municipio(id_municipio: int, dados: MunicipioUpdate):
    atual = _buscar_municipio_com_populacao(id_municipio)
    if atual is None:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    if dados.id_uf is not None and not query("SELECT id_uf FROM estados WHERE id_uf = ?", (dados.id_uf,)):
        raise HTTPException(status_code=404, detail="Estado (id_uf) não encontrado")

    novo_nome = dados.nome_municipio if dados.nome_municipio is not None else atual["nome_municipio"]
    novo_uf = dados.id_uf if dados.id_uf is not None else atual["id_uf"]
    _execute(
        "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
        (novo_nome, novo_uf, id_municipio),
    )

    if dados.populacao is not None:
        _execute(
            """
            INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
            VALUES (?, ?, 'populacao_residente_estimada', ?, 'pessoas', 'cadastro manual')
            ON CONFLICT(id_municipio, ano) DO UPDATE SET valor = excluded.valor
            """,
            (id_municipio, _ano_referencia(), dados.populacao),
        )

    return _buscar_municipio_com_populacao(id_municipio)


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    if not query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)):
        raise HTTPException(status_code=404, detail="Município não encontrado")

    _execute("DELETE FROM registros_gestor WHERE id_municipio = ?", (id_municipio,))
    _execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
    _execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    return {"status": "ok", "mensagem": f"Município {id_municipio} removido"}

#CRUD de cadastro (registros_gestor)

def _buscar_registro(id_registro: int) -> dict | None:
    rows = query(
        """
        SELECT id_registro, id_municipio, status, prioridade, observacao, responsavel, data_registro
        FROM registros_gestor WHERE id_registro = ?
        """,
        (id_registro,),
    )
    return rows[0] if rows else None


@router.post("/municipios/{id_municipio}/registros", response_model=RegistroGestor, status_code=201)
def criar_registro(id_municipio: int, dados: RegistroGestorCreate):
    if not query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)):
        raise HTTPException(status_code=404, detail="Município não encontrado")

    novo_id = _execute(
        """
        INSERT INTO registros_gestor (id_municipio, status, prioridade, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?)
        """,
        (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel),
    )
    return _buscar_registro(novo_id)


@router.get("/municipios/{id_municipio}/registros", response_model=list[RegistroGestor])
def listar_registros(id_municipio: int):
    if not query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,)):
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return query(
        """
        SELECT id_registro, id_municipio, status, prioridade, observacao, responsavel, data_registro
        FROM registros_gestor WHERE id_municipio = ? ORDER BY data_registro DESC
        """,
        (id_municipio,),
    )


@router.put("/registros/{id_registro}", response_model=RegistroGestor)
def atualizar_registro(id_registro: int, dados: RegistroGestorUpdate):
    atual = _buscar_registro(id_registro)
    if atual is None:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    _execute(
        """
        UPDATE registros_gestor
        SET status = ?, prioridade = ?, observacao = ?, responsavel = ?
        WHERE id_registro = ?
        """,
        (
            dados.status if dados.status is not None else atual["status"],
            dados.prioridade if dados.prioridade is not None else atual["prioridade"],
            dados.observacao if dados.observacao is not None else atual["observacao"],
            dados.responsavel if dados.responsavel is not None else atual["responsavel"],
            id_registro,
        ),
    )
    return _buscar_registro(id_registro)


@router.delete("/registros/{id_registro}")
def remover_registro(id_registro: int):
    if _buscar_registro(id_registro) is None:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    _execute("DELETE FROM registros_gestor WHERE id_registro = ?", (id_registro,))
    return {"status": "ok", "mensagem": f"Registro {id_registro} removido"}