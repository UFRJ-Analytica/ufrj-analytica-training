"""
API do sistema de acompanhamento populacional (IBGE) para gestores.

O endpoint `/regioes` está implementado como exemplo do padrão a seguir:
query -> banco -> validação com Pydantic -> retorno.

Os endpoints de dados básicos, análise e cadastro estão implementados
com SQLite + FastAPI.

Para rodar:
    uvicorn app.main:app --reload

Depois acesse a documentação interativa em http://127.0.0.1:8000/docs
"""
import importlib
import pkgutil

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import endpoints
from app.database import get_connection, query
from app.schemas import (
    AtualizarMunicipioPayload,
    AtualizarRegistroPayload,
    CriarMunicipioPayload,
    CriarRegistroPayload,
    Regiao,
)

app = FastAPI(
    title="UFRJ Analytica - Sistema de Acompanhamento Populacional",
    description="API construída durante a capacitação de WebDev para Ciência de Dados.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def incluir_endpoints_dos_trainees() -> None:
    """Importa automaticamente rotas criadas em app/endpoints/*.py."""
    for module_info in pkgutil.iter_modules(endpoints.__path__):
        module = importlib.import_module(f"app.endpoints.{module_info.name}")

        router = getattr(module, "router", None)
        if router is not None:
            app.include_router(router)
            continue

        trainee_app = getattr(module, "app", None)
        if isinstance(trainee_app, FastAPI):
            for route in trainee_app.router.routes:
                if route.path not in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
                    app.router.routes.append(route)


incluir_endpoints_dos_trainees()


def garantir_tabela_registros() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registros_municipio (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                id_municipio INTEGER NOT NULL,
                status TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                observacao TEXT,
                responsavel TEXT,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def obter_id_indicador_populacao(conn) -> int:
    row = conn.execute(
        """
        SELECT id_indicador
        FROM indicadores
        WHERE LOWER(nome_indicador) LIKE '%popula%'
        ORDER BY id_indicador
        LIMIT 1
        """
    ).fetchone()
    if row is not None:
        return int(row["id_indicador"])

    cursor = conn.execute(
        "INSERT INTO indicadores (nome_indicador) VALUES (?)",
        ("População estimada",),
    )
    conn.commit()
    return int(cursor.lastrowid)


garantir_tabela_registros()


@app.get("/", tags=["status"])
def root():
    return {"status": "ok", "mensagem": "API no ar. Veja /docs para a documentação."}


# ---------------------------------------------------------------------------
# Exemplo pronto, use como referência.
# ---------------------------------------------------------------------------
@app.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows


# ---------------------------------------------------------------------------
# Consulta e análise: endpoints que alimentam os gráficos do painel.
# ---------------------------------------------------------------------------

@app.get("/estados", tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    sql = "SELECT id_uf, nome_uf, sigla_uf, id_regiao FROM estados"
    params: tuple = ()
    if id_regiao is not None:
        sql += " WHERE id_regiao = ?"
        params = (id_regiao,)
    sql += " ORDER BY nome_uf"
    return query(sql, params)


@app.get("/municipios", tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    conditions = []
    params = []

    if nome:
        conditions.append("LOWER(m.nome_municipio) LIKE ?")
        params.append(f"%{nome.lower()}%")
    if id_uf is not None:
        conditions.append("m.id_uf = ?")
        params.append(id_uf)

    where_clause = ""
    if conditions:
        where_clause = f"WHERE {' AND '.join(conditions)}"

    sql = f"""
        SELECT
            m.id_municipio,
            m.nome_municipio,
            e.id_uf,
            e.sigla_uf,
            e.nome_uf,
            fi.valor AS populacao,
            fi.ano
        FROM municipios m
        JOIN estados e ON e.id_uf = m.id_uf
        LEFT JOIN fato_indicador_municipal fi
            ON fi.id_municipio = m.id_municipio
           AND fi.ano = (
               SELECT MAX(fi2.ano)
               FROM fato_indicador_municipal fi2
               WHERE fi2.id_municipio = m.id_municipio
           )
        {where_clause}
        ORDER BY m.nome_municipio
        LIMIT ?
    """
    params.append(limit)
    return query(sql, tuple(params))


@app.get("/populacao/top-municipios", tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    return query(
        """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            e.sigla_uf,
            e.nome_uf,
            r.nome_regiao,
            fi.valor AS populacao,
            fi.ano
        FROM fato_indicador_municipal fi
        JOIN municipios m ON m.id_municipio = fi.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        ORDER BY fi.valor DESC
        LIMIT ?
        """,
        (limit,),
    )


@app.get("/populacao/por-regiao", tags=["análise"])
def populacao_por_regiao():
    return query(
        """
        SELECT
            r.id_regiao,
            r.sigla_regiao,
            r.nome_regiao,
            SUM(fi.valor) AS populacao_total
        FROM fato_indicador_municipal fi
        JOIN municipios m ON m.id_municipio = fi.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        GROUP BY r.id_regiao, r.sigla_regiao, r.nome_regiao
        ORDER BY populacao_total DESC
        """
    )


@app.get("/populacao/por-uf", tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT
            e.id_uf,
            e.sigla_uf,
            e.nome_uf,
            e.id_regiao,
            SUM(fi.valor) AS populacao_total
        FROM fato_indicador_municipal fi
        JOIN municipios m ON m.id_municipio = fi.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
    """
    params: tuple = ()
    if id_regiao is not None:
        sql += " WHERE e.id_regiao = ?"
        params = (id_regiao,)
    sql += " GROUP BY e.id_uf, e.sigla_uf, e.nome_uf, e.id_regiao ORDER BY populacao_total DESC"
    return query(sql, params)


@app.get("/populacao/distribuicao", tags=["análise"])
def distribuicao_populacional():
    return query(
        """
        SELECT fi.valor AS populacao
        FROM fato_indicador_municipal fi
        ORDER BY fi.valor
        """
    )


@app.get("/populacao/dispersao-uf", tags=["análise"])
def dispersao_por_uf():
    return query(
        """
        SELECT
            e.id_uf,
            e.sigla_uf,
            e.nome_uf,
            COUNT(DISTINCT m.id_municipio) AS quantidade_municipios,
            ROUND(AVG(fi.valor), 2) AS populacao_media_municipio
        FROM estados e
        JOIN municipios m ON m.id_uf = e.id_uf
        JOIN fato_indicador_municipal fi ON fi.id_municipio = m.id_municipio
        GROUP BY e.id_uf, e.sigla_uf, e.nome_uf
        ORDER BY populacao_media_municipio DESC
        """
    )


@app.get("/populacao/heatmap-regiao-porte", tags=["análise"])
def heatmap_regiao_porte():
    return query(
        """
        SELECT
            r.nome_regiao,
            CASE
                WHEN fi.valor >= 1000000 THEN 'grande'
                WHEN fi.valor >= 200000 THEN 'medio'
                ELSE 'pequeno'
            END AS porte,
            COUNT(*) AS quantidade_municipios
        FROM fato_indicador_municipal fi
        JOIN municipios m ON m.id_municipio = fi.id_municipio
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        GROUP BY r.nome_regiao, porte
        ORDER BY r.nome_regiao, porte
        """
    )


@app.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    rows = query(
        """
        SELECT
            (SELECT COUNT(*) FROM regioes) AS total_regioes,
            (SELECT COUNT(*) FROM estados) AS total_estados,
            (SELECT COUNT(*) FROM municipios) AS total_municipios,
            (SELECT SUM(valor) FROM fato_indicador_municipal) AS populacao_total,
            (SELECT ROUND(AVG(valor), 2) FROM fato_indicador_municipal) AS media_populacao_municipio
        """
    )
    return rows[0]


@app.get("/municipios/{id_municipio}", tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    rows = query(
        """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            e.id_uf,
            e.sigla_uf,
            e.nome_uf,
            r.id_regiao,
            r.sigla_regiao,
            r.nome_regiao,
            fi.ano,
            fi.valor AS populacao
        FROM municipios m
        JOIN estados e ON e.id_uf = m.id_uf
        JOIN regioes r ON r.id_regiao = e.id_regiao
        LEFT JOIN fato_indicador_municipal fi ON fi.id_municipio = m.id_municipio
        WHERE m.id_municipio = ?
        ORDER BY fi.ano DESC
        """,
        (id_municipio,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return rows


@app.post("/municipios", tags=["dados básicos"])
def criar_municipio(payload: CriarMunicipioPayload):
    conn = get_connection()
    try:
        estado = conn.execute("SELECT 1 FROM estados WHERE id_uf = ?", (payload.id_uf,)).fetchone()
        if estado is None:
            raise HTTPException(status_code=404, detail="Estado não encontrado")

        max_id_row = conn.execute("SELECT COALESCE(MAX(id_municipio), 0) AS max_id FROM municipios").fetchone()
        novo_id = int(max_id_row["max_id"]) + 1

        conn.execute(
            "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
            (novo_id, payload.nome_municipio, payload.id_uf),
        )

        if payload.populacao_inicial is not None:
            indicador_id = obter_id_indicador_populacao(conn)
            conn.execute(
                """
                INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor)
                VALUES (?, ?, ?, ?)
                """,
                (novo_id, indicador_id, payload.ano_referencia, payload.populacao_inicial),
            )

        conn.commit()
        return {"id_municipio": novo_id, "mensagem": "Município criado com sucesso"}
    finally:
        conn.close()


@app.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, payload: AtualizarMunicipioPayload):
    conn = get_connection()
    try:
        existente = conn.execute(
            "SELECT id_municipio FROM municipios WHERE id_municipio = ?",
            (id_municipio,),
        ).fetchone()
        if existente is None:
            raise HTTPException(status_code=404, detail="Município não encontrado")

        if payload.id_uf is not None:
            estado = conn.execute("SELECT 1 FROM estados WHERE id_uf = ?", (payload.id_uf,)).fetchone()
            if estado is None:
                raise HTTPException(status_code=404, detail="Estado não encontrado")

        campos = []
        params = []
        if payload.nome_municipio is not None:
            campos.append("nome_municipio = ?")
            params.append(payload.nome_municipio)
        if payload.id_uf is not None:
            campos.append("id_uf = ?")
            params.append(payload.id_uf)

        if campos:
            params.append(id_municipio)
            conn.execute(
                f"UPDATE municipios SET {', '.join(campos)} WHERE id_municipio = ?",
                tuple(params),
            )

        if payload.populacao is not None:
            indicador_id = obter_id_indicador_populacao(conn)
            row = conn.execute(
                """
                SELECT 1
                FROM fato_indicador_municipal
                WHERE id_municipio = ? AND id_indicador = ? AND ano = ?
                """,
                (id_municipio, indicador_id, payload.ano_referencia),
            ).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO fato_indicador_municipal (id_municipio, id_indicador, ano, valor)
                    VALUES (?, ?, ?, ?)
                    """,
                    (id_municipio, indicador_id, payload.ano_referencia, payload.populacao),
                )
            else:
                conn.execute(
                    """
                    UPDATE fato_indicador_municipal
                    SET valor = ?
                    WHERE id_municipio = ? AND id_indicador = ? AND ano = ?
                    """,
                    (payload.populacao, id_municipio, indicador_id, payload.ano_referencia),
                )

        conn.commit()
        return {"mensagem": "Município atualizado com sucesso"}
    finally:
        conn.close()


@app.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    conn = get_connection()
    try:
        existente = conn.execute(
            "SELECT 1 FROM municipios WHERE id_municipio = ?",
            (id_municipio,),
        ).fetchone()
        if existente is None:
            raise HTTPException(status_code=404, detail="Município não encontrado")

        conn.execute("DELETE FROM registros_municipio WHERE id_municipio = ?", (id_municipio,))
        conn.execute("DELETE FROM fato_indicador_municipal WHERE id_municipio = ?", (id_municipio,))
        conn.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
        conn.commit()
        return {"mensagem": "Município removido com sucesso"}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------

@app.post("/municipios/{id_municipio}/registros", tags=["cadastro"])
def criar_registro(id_municipio: int, payload: CriarRegistroPayload):
    conn = get_connection()
    try:
        municipio = conn.execute(
            "SELECT 1 FROM municipios WHERE id_municipio = ?",
            (id_municipio,),
        ).fetchone()
        if municipio is None:
            raise HTTPException(status_code=404, detail="Município não encontrado")

        cursor = conn.execute(
            """
            INSERT INTO registros_municipio (id_municipio, status, prioridade, observacao, responsavel)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                id_municipio,
                payload.status,
                payload.prioridade,
                payload.observacao,
                payload.responsavel,
            ),
        )
        conn.commit()
        return {"id_registro": cursor.lastrowid, "mensagem": "Registro criado com sucesso"}
    finally:
        conn.close()


@app.get("/municipios/{id_municipio}/registros", tags=["cadastro"])
def listar_registros(id_municipio: int):
    rows = query(
        """
        SELECT
            id_registro,
            id_municipio,
            status,
            prioridade,
            observacao,
            responsavel,
            criado_em,
            atualizado_em
        FROM registros_municipio
        WHERE id_municipio = ?
        ORDER BY atualizado_em DESC
        """,
        (id_municipio,),
    )
    return rows


@app.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, payload: AtualizarRegistroPayload):
    campos = []
    params = []
    if payload.status is not None:
        campos.append("status = ?")
        params.append(payload.status)
    if payload.prioridade is not None:
        campos.append("prioridade = ?")
        params.append(payload.prioridade)
    if payload.observacao is not None:
        campos.append("observacao = ?")
        params.append(payload.observacao)
    if payload.responsavel is not None:
        campos.append("responsavel = ?")
        params.append(payload.responsavel)

    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    conn = get_connection()
    try:
        existente = conn.execute(
            "SELECT 1 FROM registros_municipio WHERE id_registro = ?",
            (id_registro,),
        ).fetchone()
        if existente is None:
            raise HTTPException(status_code=404, detail="Registro não encontrado")

        params.extend([id_registro])
        conn.execute(
            f"""
            UPDATE registros_municipio
            SET {', '.join(campos)}, atualizado_em = CURRENT_TIMESTAMP
            WHERE id_registro = ?
            """,
            tuple(params),
        )
        conn.commit()
        return {"mensagem": "Registro atualizado com sucesso"}
    finally:
        conn.close()


@app.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM registros_municipio WHERE id_registro = ?", (id_registro,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return {"mensagem": "Registro removido com sucesso"}
    finally:
        conn.close()
