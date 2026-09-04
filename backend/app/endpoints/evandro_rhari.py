from fastapi import APIRouter, HTTPException, Query

from schemas import *
from database import query, alter


# Criando Router
router = APIRouter(prefix='/evandro-rhari', tags=['evandro_rhari'])

@router.get('/status')
def status():
    return {'status': 'ok'}


# Copiando o endpoint de exemplo apenas para manter a consistência no prefixo.
@router.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows


# ---------------------------------------------------------------------------
# Consulta e análise: endpoints que alimentam os gráficos do painel.
# ---------------------------------------------------------------------------

@router.get("/estados", tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    rows = query("""SELECT uf.id_uf, uf.sigla_uf, uf.nome_uf, reg.id_regiao, reg.sigla_regiao
                    FROM estados as uf
                        NATURAL JOIN regioes reg
                    ORDER BY uf.id_uf;
                """)
    return rows


@router.get("/municipios", tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    condicoes = []

    if nome:
        condicoes.append(f" nome_municipio LIKE '%{nome}%' ")
    if id_uf:
        condicoes.append(f" id_uf = {id_uf}")

    where = f'WHERE {' AND '.join(condicoes)}' if condicoes else ""
    
    rows = query(f"SELECT * FROM municipios {where} ORDER BY id_municipio LIMIT {limit};")
    return rows


@router.get("/populacao/top-municipios", tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    rows = query("SELECT muni.id_municipio, muni.nome_municipio, muni.id_uf, pop.valor População " \
                    "FROM municipios muni " \
                        "NATURAL JOIN populacao_municipal pop " \
                    "ORDER BY População DESC " \
                   f"LIMIT {limit};"
    )
    return rows


@router.get("/populacao/por-regiao", tags=["análise"])
def populacao_por_regiao():
    rows = query("SELECT DISTINCT reg.id_regiao, reg.nome_regiao, SUM(pop.valor) populacao " \
                    "FROM regioes reg " \
                        "NATURAL JOIN estados " \
                        "NATURAL JOIN municipios " \
                        "NATURAL JOIN populacao_municipal pop " \
                "GROUP BY reg.id_regiao " \
                "ORDER BY reg.id_regiao;"
            )
    return rows



@router.get("/populacao/por-uf", tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    """TODO: população total por estado, com filtro opcional por região."""

    condicao = ""
    if id_regiao:
        condicao = f'WHERE regioes.id_regiao = {id_regiao}'

    rows = query(f"SELECT est.id_uf, est.nome_uf, est.sigla_uf, SUM(pop.valor) populacao_total " \
                    "FROM populacao_municipal pop " \
                        "NATURAL JOIN municipios " \
                        "NATURAL JOIN estados est " \
                        "NATURAL JOIN regioes " \
                        f"{condicao} " \
                    "GROUP BY est.id_uf "
                 )
    return rows


@router.get("/populacao/distribuicao", tags=["análise"])
def distribuicao_populacional():
    """Valores de população de todos os municípios, para um histograma."""
    rows = query("SELECT muni.id_municipio, muni.nome_municipio, pop.valor populacao " \
                    "FROM municipios muni " \
                        "NATURAL JOIN populacao_municipal pop " \
                    "ORDER BY muni.id_municipio"
                 )
    return rows


@router.get("/populacao/dispersao-uf", tags=["análise"])
def dispersao_por_uf():
    """TODO: por estado, quantidade de municípios x população média, para um scatter."""
    rows = query("SELECT est.id_uf, est.nome_uf, " \
                        "COUNT(muni.id_municipio) quantidade_municipios, AVG(pop.valor) populacao_media  " \
                    "FROM estados est " \
                        "NATURAL JOIN municipios muni " \
                        "NATURAL JOIN populacao_municipal pop " \
                    "GROUP BY est.id_uf " \
                    "ORDER BY est.id_uf"
                 )
    return rows


@router.get("/populacao/heatmap-regiao-porte", tags=["análise"])
def heatmap_regiao_porte():
    """TODO: quantidade de municípios por região x porte (pequeno/médio/grande),
    para um mapa de calor. Definam vocês os limites de população de cada porte."""
    media = query("SELECT COUNT(muni.id_municipio)/COUNT(DISTINCT reg.id_regiao) media " \
                    "FROM regioes reg " \
                        "NATURAL JOIN estados " \
                        "NATURAL JOIN municipios muni "
                )[0]['media']
    rows = query("SELECT reg.id_regiao, reg.sigla_regiao, reg.nome_regiao, COUNT(muni.id_municipio) qtd_municipios, " \
                    "CASE " \
                        f"WHEN COUNT(muni.id_municipio) < {media*0.75} THEN 'pequeno' " \
                        f"WHEN COUNT(muni.id_municipio) < {media*1.25}  THEN 'medio' " \
                        f"ELSE                                              'grande' " \
                    "END AS porte "
                    "FROM regioes reg " \
                        "NATURAL JOIN estados " \
                        "NATURAL JOIN municipios muni " \
                    "GROUP BY reg.id_regiao"
                )
    return rows



@router.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    """TODO: números resumo para os KPIs do topo do painel."""
    rows = query("SELECT COUNT(DISTINCT muni.id_municipio) total_municipio, " \
                        "COUNT(DISTINCT est.id_uf) total_estado, " \
                        "COUNT(DISTINCT reg.id_regiao) total_regioes, " \
                        "SUM(pop.valor) populacao_total, " \
                        "pop.ano ano " \
                    "FROM regioes reg " \
                        "NATURAL JOIN estados est " \
                        "NATURAL JOIN municipios muni " \
                        "NATURAL JOIN populacao_municipal pop" \
                            )
    return rows


@router.get("/municipios/{id_municipio}", tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    """dados completos de um município, ou 404 se não existir."""
    row = query(f'SELECT * FROM municipios WHERE municipios.id_municipio = {id_municipio}')

    if row:
        return row[0]
    else:
        raise HTTPException(status_code=404, detail='Id não consta na tabela de municipios')


@router.post("/municipios", tags=["dados básicos"])
def criar_municipio(municipio: Municipio):
    """cadastrar um novo município (nome, estado e população inicial).
    Como não existe um id_municipio real do IBGE pra um município novo,
    gerem um (por exemplo, MAX(id_municipio) + 1)."""

    if municipio.id_municipio:
        rows = query(f"SELECT id_municipio FROM municipios WHERE id_municipio = {municipio.id_municipio}")

        if rows:
            raise HTTPException(400, 'id já consta na base de dados')
    else:
        municipio.id_municipio = query("SELECT COUNT(*) count FROM municipios")[0]['count'] + 1

    return alter("INSERT INTO municipios(id_municipio, nome_municipio, id_uf) " \
                    f"VALUES({municipio.id_municipio}, '{municipio.nome_municipio}', {municipio.id_municipio})" 
            )


@router.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, municipio: MunicipioUpdate):
    """atualizar nome, estado e/ou população de um município existente."""
    rows = query(f"SELECT id_municipio FROM municipios WHERE id_municipio = {id_municipio}")
    if not rows:
            raise HTTPException(404, 'id não consta na tabela de municipios')

    if municipio.id_municipio:
        id_municipio = municipio.id_municipio

    sets = []
    for field,value in municipio.model_dump().items():
        if value:
            if type(value) == str:
                value = f"'{value}'"
            sets.append(f"{field}={value}")

    if sets:
        sets = "SET " + ", ".join(sets)
        return alter("UPDATE municipios " \
                        f"{sets} " \
                        f"WHERE id_municipio = {id_municipio}"
                    )
    raise HTTPException(status_code=400, detail="Coloque algum valor para alterar")


@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    """remover um município (e os dados dependentes dele)."""

    rows = query(f"SELECT id_municipio FROM municipios WHERE id_municipio = {id_municipio}")
    if not rows:
        raise HTTPException(404, 'id não consta na tabela de municipios')
    if not alter(f"DELETE FROM municipios WHERE id_municipio={id_municipio}")["success"]:
        return False

    rows = query(f"SELECT id_municipio FROM populacao_municipal WHERE id_municipio = {id_municipio}")
    if rows:
        alter(f"DELETE FROM populacao_municipal WHERE id_municipio={id_municipio}")
    return True


# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------

@router.post("/municipios/{id_municipio}/registros", tags=["cadastro"])
def criar_registro(id_municipio: int, cadastro: CadastroMunicipal):
    """TODO: criar um novo registro de cadastro para o município."""

    if id_municipio:
        rows = query(f"SELECT id_municipio FROM municipios WHERE id_municipio = {id_municipio}")
        if not rows:
            raise HTTPException(404, 'id não consta na tabela de municipios')

    status = alter("INSERT INTO cadastros_municipais(status_atual, prioridade, responsavel, id_municipio) " \
                        f"VALUES('{cadastro.status_atual}', " \
                                f"'{cadastro.prioridade}', " \
                                f"'{cadastro.responsavel}', " \
                                f"{cadastro.id_municipio})"
                )
    if not status["success"]:
        raise HTTPException(500, status["detail"])

@router.get("/municipios/{id_municipio}/registros", tags=["cadastro"])
def listar_registros(id_municipio: int):
    """listar os registros de cadastro de um município."""
    rows = query(f"SELECT * FROM cadastros_municipais WHERE id_municipio={id_municipio}")
    return rows


@router.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, cadastro: CadastroMunicipalUpdate):
    """atualizar um registro de cadastro existente."""
    rows = query(f"SELECT id_cadastro_municipal FROM cadastros_municipais WHERE id_cadastro_municipal={id_registro}")
    if not rows:
        HTTPException(400, "id não consta na tabela de cadastros municipais")


    sets = []
    for field,value in cadastro.model_dump().items():
        if value:
            if type(value) == str:
                value = f"'{value}'"
            sets.append(f"{field}={value}")


    if sets:
        sets = "SET " + ", ".join(sets)
        status = alter("UPDATE cadastros_municipais " \
                        f"{sets} " \
                        f"WHERE id_cadastro_municipal = {id_registro}"
                    )
        if not status:
            raise HTTPException(500, status["detail"])
        return True
    raise HTTPException(status_code=400, detail="Coloque algum valor para alterar")


@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    """remover um registro de cadastro."""
    rows = query(f"SELECT id_cadastro_municipal FROM cadastros_municipais WHERE id_cadastro_municipal = {id_registro}")
    if not rows:
        raise HTTPException(404, 'id não consta na tabela de cadastros municipais')
    if not alter(f"DELETE FROM cadastros_municipais WHERE id_cadastro_municipal={id_registro}"):
        return False
    return True