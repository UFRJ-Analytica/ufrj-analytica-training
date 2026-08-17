from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection, query
from app.schemas import Regiao, Municipio, Registro, MunicipioOut, RegistroOut, Estado

ANO_REF = 2025

router = APIRouter(
    prefix="/pedro-ferrari",
    tags=["Pedro Ferrari"]
)

@router.get("/status")
def status():
    return {"status": "ok"}

@router.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows


@router.get("/total-municipios")
def total_municipios():
    resultado = query(
        """
        SELECT COUNT(*) AS total_municipios
        FROM municipios
        """
    )

    return resultado[0]


@router.get("/estados", response_model=list[Estado], tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    if id_regiao is None:
        rows = query("SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados ORDER BY nome_uf")
    else:
        rows = query("SELECT id_uf, sigla_uf, nome_uf, id_regiao FROM estados WHERE id_regiao = ? ORDER BY nome_uf", (id_regiao,))
    return rows


@router.get("/municipios",  response_model=list[MunicipioOut], tags=["dados básicos"])
def listar_municipios(nome: str | None = Query(default=None), id_uf: int | None = Query(default=None), limit: int = Query(default=50, ge=1, le=500),):
    if nome is None and id_uf is None:
        rows = query(
            """
            SELECT
                id_municipio,
                nome_municipio,
                id_uf
            FROM municipios
            ORDER BY nome_municipio
            LIMIT ?
            """,
            (limit,)
        )

    elif nome is None and id_uf is not None:
        rows = query(
            """
            SELECT
                id_municipio,
                nome_municipio,
                id_uf
            FROM municipios
            WHERE id_uf = ?
            ORDER BY nome_municipio
            LIMIT ?
            """,
            (id_uf, limit)
        )

    elif nome is not None and id_uf is None:
        rows = query(
            """
            SELECT
                id_municipio,
                nome_municipio,
                id_uf
            FROM municipios
            WHERE nome_municipio LIKE ?
            ORDER BY nome_municipio
            LIMIT ?
            """,
            (f"%{nome}%", limit)
        )

    else:
        rows = query(
            """
            SELECT
                id_municipio,
                nome_municipio,
                id_uf
            FROM municipios
            WHERE nome_municipio LIKE ?
              AND id_uf = ?
            ORDER BY nome_municipio
            LIMIT ?
            """,
            (f"%{nome}%", id_uf, limit)
        )

    return rows


@router.get("/populacao/top-municipios", tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    rows = query(
        """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            CAST(pm.valor AS INTEGER) AS populacao
        FROM municipios AS m
        INNER JOIN populacao_municipal AS pm
            ON pm.id_municipio = m.id_municipio 
        WHERE pm.ano = ?
        ORDER BY pm.valor DESC
        LIMIT ?
        """,
        (ANO_REF, limit)
    )

    return rows



@router.get("/populacao/por-regiao", tags=["análise"])
def populacao_por_regiao():
    rows = query(
            """
            SELECT
                r.nome_regiao,
                CAST(SUM(pm.valor) AS INTEGER) AS populacao
            FROM regioes AS r
            INNER JOIN estados AS e
                ON r.id_regiao = e.id_regiao
            INNER JOIN municipios AS m 
                ON m.id_uf = e.id_uf
            INNER JOIN populacao_municipal as pm
                ON pm.id_municipio = m.id_municipio  
            WHERE pm.ano = ? 
            GROUP BY r.nome_regiao
            """,
            (ANO_REF, )
    )

    return rows


@router.get("/populacao/por-uf", tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    if id_regiao is None:
        rows = query(
                """
                SELECT
                    e.id_uf,
                    e.sigla_uf,
                    e.nome_uf,
                    r.nome_regiao,
                    CAST(SUM(pm.valor) AS INTEGER) AS populacao_total
                FROM estados AS e
                INNER JOIN regioes as r
                    ON e.id_regiao = r.id_regiao
                INNER JOIN municipios AS m 
                    ON m.id_uf = e.id_uf
                INNER JOIN populacao_municipal as pm
                    ON pm.id_municipio = m.id_municipio
                WHERE pm.ano = ?   
                GROUP BY e.nome_uf, e.id_uf
                ORDER BY populacao_total DESC
                """,
                (ANO_REF, )
        )
    else:
        rows = query(
                """
                SELECT
                    e.id_uf,
                    e.sigla_uf,
                    e.nome_uf,
                    r.nome_regiao,
                    CAST(SUM(pm.valor) AS INTEGER) AS populacao_total
                FROM estados AS e
                INNER JOIN regioes as r
                    ON e.id_regiao = r.id_regiao
                INNER JOIN municipios AS m 
                    ON m.id_uf = e.id_uf
                INNER JOIN populacao_municipal as pm
                    ON pm.id_municipio = m.id_municipio
                WHERE r.id_regiao = ? AND pm.ano = ? 
                GROUP BY e.nome_uf, e.sigla_uf, r.nome_regiao
                ORDER BY populacao_total DESC
                """, (id_regiao, ANO_REF)
        )

    return rows    
    
    


@router.get("/populacao/distribuicao", tags=["análise"])
def distribuicao_populacional():
    rows = query(
        """
        SELECT
            m.id_municipio,
            m.nome_municipio,
            CAST(pm.valor AS INTEGER) AS populacao
        FROM municipios AS m
        INNER JOIN populacao_municipal AS pm
            ON pm.id_municipio = m.id_municipio
        WHERE pm.valor IS NOT NULL AND pm.ano = ?
        ORDER BY populacao
        """,
        (ANO_REF,)
    )

    return rows


@router.get("/populacao/dispersao-uf", tags=["análise"])
def dispersao_por_uf():
    rows = query(
        """
        SELECT
            e.id_uf,
            e.sigla_uf,
            e.nome_uf,
            r.nome_regiao,
            COUNT(DISTINCT m.id_municipio) AS quantidade_municipios,
            CAST(AVG(pm.valor) AS INTEGER) AS populacao_media
        FROM estados AS e
        INNER JOIN municipios AS m
            ON m.id_uf = e.id_uf
        INNER JOIN regioes AS r
            ON r.id_regiao = e.id_regiao
        INNER JOIN populacao_municipal AS pm
            ON pm.id_municipio = m.id_municipio
        WHERE pm.valor IS NOT NULL AND pm.ano = ?
        GROUP BY
            e.id_uf,
            e.sigla_uf,
            e.nome_uf,
            r.nome_regiao
        ORDER BY quantidade_municipios DESC
        """,
        (ANO_REF,)
    )

    return rows

@router.get("/populacao/heatmap-regiao-porte", tags=["análise"])
def heatmap_regiao_porte():
    rows = query(
        """
        SELECT
            r.nome_regiao,
            CASE
                WHEN pm.valor < 20000 THEN 'Pequeno'
                WHEN pm.valor < 100000 THEN 'Médio'
                ELSE 'Grande'
            END AS porte,
            COUNT(DISTINCT m.id_municipio) AS quantidade_municipios
        FROM regioes AS r
        INNER JOIN estados AS e
            ON e.id_regiao = r.id_regiao
        INNER JOIN municipios AS m
            ON m.id_uf = e.id_uf
        INNER JOIN populacao_municipal AS pm
            ON pm.id_municipio = m.id_municipio
        WHERE pm.valor IS NOT NULL AND pm.ano = ?
        GROUP BY
            r.nome_regiao,
            CASE
                WHEN pm.valor < 20000 THEN 'Pequeno'
                WHEN pm.valor < 100000 THEN 'Médio'
                ELSE 'Grande'
            END
        ORDER BY
            r.nome_regiao,
            porte
        """,
        (ANO_REF,)
    )

    return rows


@router.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    rows = query(
        """
        WITH ano_referencia AS (
            SELECT ? AS ano
        ),

        populacao_atual AS (
            SELECT
                pm.id_municipio,
                MAX(CAST(pm.valor AS REAL)) AS populacao
            FROM populacao_municipal AS pm
            INNER JOIN ano_referencia AS ar
                ON pm.ano = ar.ano
            GROUP BY pm.id_municipio
        )

        SELECT
            (
                SELECT COUNT(*)
                FROM municipios
            ) AS total_municipios,

            (
                SELECT COUNT(*)
                FROM estados
            ) AS total_estados,

            CAST(
                (
                    SELECT SUM(populacao)
                    FROM populacao_atual
                ) AS INTEGER
            ) AS populacao_total,

            (
                SELECT ano
                FROM ano_referencia
            ) AS ano_referencia,

            (
                SELECT m.nome_municipio
                FROM populacao_atual AS pa
                INNER JOIN municipios AS m
                    ON m.id_municipio = pa.id_municipio
                ORDER BY pa.populacao DESC
                LIMIT 1
            ) AS municipio_mais_populoso,

            CAST(
                (
                    SELECT MAX(populacao)
                    FROM populacao_atual
                ) AS INTEGER
            ) AS populacao_municipio_mais_populoso
        """,
        (ANO_REF,)
    )

    return rows[0]


@router.get("/municipios/{id_municipio}", response_model=MunicipioOut, tags=["dados básicos"])
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
            r.nome_regiao,

            pm.ano,
            CAST(pm.valor AS INTEGER) AS populacao

        FROM municipios AS m

        INNER JOIN estados AS e
            ON e.id_uf = m.id_uf

        INNER JOIN regioes AS r
            ON r.id_regiao = e.id_regiao

        LEFT JOIN populacao_municipal AS pm
            ON pm.id_municipio = m.id_municipio AND pm.ano = ?

        WHERE m.id_municipio = ?
        """,
        (ANO_REF, id_municipio)
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado"
        )

    return rows[0]


@router.post("/municipios", response_model=MunicipioOut, tags=["dados básicos"])
def criar_municipio(dados: Municipio):

    conn = get_connection()

    try:
        estado = conn.execute(
            """
            SELECT id_uf
            FROM estados
            WHERE id_uf = ?
            """,
            (dados.id_uf,)
        ).fetchone()

        if estado is None:
            raise HTTPException(
                status_code=404,
                detail="Estado não encontrado"
            )

        # novo ID
        resultado = conn.execute(
            """
            SELECT COALESCE(MAX(id_municipio), 0) + 1 AS novo_id
            FROM municipios
            """
        ).fetchone()

        novo_id = resultado["novo_id"]

        # Cadastra município
        conn.execute(
            """
            INSERT INTO municipios (
                id_municipio,
                nome_municipio,
                id_uf
            )
            VALUES (?, ?, ?)
            """,
            (novo_id, dados.nome_municipio, dados.id_uf)
        )

        # Cadastra população 
        conn.execute(
            """
            INSERT INTO populacao_municipal (id_municipio, ano, valor)
            VALUES (?, ?, ?)
            """,
            (novo_id, ANO_REF, dados.populacao_inicial)
        )

        conn.commit()

        return {
            "id_municipio": novo_id,
            "nome_municipio": dados.nome_municipio,
            "id_uf": dados.id_uf,
            "populacao": dados.populacao_inicial,
            "ano": ANO_REF
        }

    finally:
        conn.close()


@router.put("/municipios/{id_municipio}",  response_model=MunicipioOut, tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, dados: Municipio):

    conn = get_connection()

    try:
        # verifica se o município existe
        municipio = conn.execute(
            """
            SELECT id_municipio
            FROM municipios
            WHERE id_municipio = ?
            """,
            (id_municipio,)
        ).fetchone()

        if municipio is None:
            raise HTTPException(
                status_code=404,
                detail="Município não encontrado"
            )

        # verifica se o novo estado existe
        estado = conn.execute(
            """
            SELECT id_uf
            FROM estados
            WHERE id_uf = ?
            """,
            (dados.id_uf,)
        ).fetchone()

        if estado is None:
            raise HTTPException(
                status_code=404,
                detail="Estado não encontrado"
            )

        # atualiza nome e estado
        conn.execute(
            """
            UPDATE municipios
            SET nome_municipio = ?,
                id_uf = ?
            WHERE id_municipio = ?
            """,
            (
                dados.nome_municipio,
                dados.id_uf,
                id_municipio
            )
        )

        # atualiza a população
        conn.execute(
            """
            UPDATE populacao_municipal
            SET valor = ?
            WHERE id_municipio = ? AND ano = ?
            """,
            (
                dados.populacao_inicial,
                id_municipio,
                ANO_REF
            )
        )

        conn.commit()

        return {
            "id_municipio": id_municipio,
            "nome_municipio": dados.nome_municipio,
            "id_uf": dados.id_uf,
            "populacao": dados.populacao_inicial,
            "ano": ANO_REF
        }

    finally:
        conn.close()


@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):

    conn = get_connection()

    try:
        # Verifica se o município existe
        municipio = conn.execute(
            """
            SELECT id_municipio
            FROM municipios
            WHERE id_municipio = ?
            """,
            (id_municipio,)
        ).fetchone()

        if municipio is None:
            raise HTTPException(
                status_code=404,
                detail="Município não encontrado"
            )
        #Primeiro tiramos o registro do gestor
        conn.execute(
            """
            DELETE FROM registros
            WHERE id_municipio = ?
            """,
            (id_municipio,)
        )

        # Remove a população ligada ao município
        conn.execute(
            """
            DELETE FROM populacao_municipal
            WHERE id_municipio = ?
            """,
            (id_municipio,)
        )

        # Depois remove o município
        conn.execute(
            """
            DELETE FROM municipios
            WHERE id_municipio = ?
            """,
            (id_municipio,)
        )

        conn.commit()

        return {
            "mensagem": "Município removido com sucesso",
            "id_municipio": id_municipio
        }

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------

@router.post("/municipios/{id_municipio}/registros", response_model=RegistroOut, tags=["cadastro"])
def criar_registro(id_municipio: int, dados: Registro):

    conn = get_connection()

    try:
        #verifica se o município existe
        municipio = conn.execute(
            """
            SELECT id_municipio
            FROM municipios
            WHERE id_municipio = ?
            """,
            (id_municipio,)
        ).fetchone()

        if municipio is None:
            raise HTTPException(
                status_code=404,
                detail="Município não encontrado"
            )

        #cria o registro
        cursor = conn.execute(
            """
            INSERT INTO registros (
                id_municipio,
                status,
                prioridade,
                observacao,
                responsavel
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel)
        )

        conn.commit()

        return {
            "id_registro": cursor.lastrowid,
            "id_municipio": id_municipio,
            "status": dados.status,
            "prioridade": dados.prioridade,
            "observacao": dados.observacao,
            "responsavel": dados.responsavel
        }

    finally:
        conn.close()


@router.get("/municipios/{id_municipio}/registros", response_model=list[RegistroOut], tags=["cadastro"])
def listar_registros(id_municipio: int):

    municipio = query(
        """
        SELECT id_municipio
        FROM municipios
        WHERE id_municipio = ?
        """,
        (id_municipio,)
    )

    if not municipio:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado"
        )

    registros = query(
        """
        SELECT
            id_registro,
            id_municipio,
            status,
            prioridade,
            observacao,
            responsavel
        FROM registros
        WHERE id_municipio = ?
        ORDER BY id_registro
        """,
        (id_municipio,)
    )

    return registros


@router.put("/registros/{id_registro}", response_model=RegistroOut, tags=["cadastro"])
def atualizar_registro(id_registro: int, dados: Registro):

    conn = get_connection()

    try:
        #verifica se o registro existe
        registro = conn.execute(
            """
            SELECT id_registro, id_municipio
            FROM registros
            WHERE id_registro = ?
            """,
            (id_registro,)
        ).fetchone()

        if registro is None:
            raise HTTPException(
                status_code=404,
                detail="Registro não encontrado"
            )

        #atualiza os dados
        conn.execute(
            """
            UPDATE registros
            SET status = ?,
                prioridade = ?,
                observacao = ?,
                responsavel = ?
            WHERE id_registro = ?
            """,
            (dados.status, dados.prioridade, dados.observacao, dados.responsavel, id_registro
)
        )

        conn.commit()

        return {
            "id_registro": id_registro,
            "id_municipio": registro["id_municipio"],
            "status": dados.status,
            "prioridade": dados.prioridade,
            "observacao": dados.observacao,
            "responsavel": dados.responsavel
        }

    finally:
        conn.close()


@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):

    conn = get_connection()

    try:
        #verifica se o registro existe
        registro = conn.execute(
            """
            SELECT id_registro
            FROM registros
            WHERE id_registro = ?
            """,
            (id_registro,)
        ).fetchone()

        if registro is None:
            raise HTTPException(
                status_code=404,
                detail="Registro não encontrado"
            )

        #remove registro
        conn.execute(
            """
            DELETE FROM registros
            WHERE id_registro = ?
            """,
            (id_registro,)
        )

        conn.commit()

        return {
            "mensagem": "Registro removido com sucesso",
            "id_registro": id_registro
        }

    finally:
        conn.close()