from csv import excel_tab

from fastapi import APIRouter, Query, HTTPException

from app.database import query, execute
from app.schemas import *

router = APIRouter(prefix="/marcelo-borges", tags=["marcelo_borges"])

@router.get("/status")
def status():
    return {"status": "ok"}

@router.get("/regioes", response_model=list[Regiao], tags=["dados básicos"])
def listar_regioes():
    rows = query("SELECT id_regiao, sigla_regiao, nome_regiao FROM regioes ORDER BY id_regiao")
    return rows


@router.get("/estados", response_model=list[Estado], tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    q = """
        select id_uf, nome_uf, sigla_uf, id_regiao from estados
        where (? is null or id_regiao=?)
        """
    rows = query(q,(id_regiao,id_regiao))
    return rows

@router.get("/municipios", response_model=list[Municipio], tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    q = """
        select m.nome_municipio, e.nome_uf, p.valor as populacao from municipios m
            inner join populacao_municipal p
            on p.id_municipio=m.id_municipio
            inner join estados e on m.id_uf = e.id_uf
            where (? is NULL or m.nome_municipio=?)
                AND (? is NULL or e.id_uf=?)
            limit ?
        """
    rows = query(q,(nome, nome, id_uf, id_uf,limit))
    return rows

@router.get("/populacao/por-regiao", response_model=list[Populacao], tags=["análise"])
def populacao_por_regiao():
    q = " \
        select r.nome_regiao as nome, sum(p.valor) as total from populacao_municipal p \
        inner join municipios m on p.id_municipio = m.id_municipio \
        inner join estados e on m.id_uf=e.id_uf \
        inner join regioes r on r.id_regiao=e.id_regiao \
        group by nome_regiao \
        "
    rows = query(q)
    return rows

@router.get("/populacao/por-uf", response_model=list[Populacao] ,tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    q = """
        select e.nome_uf as nome, sum(p.valor) as total
        from populacao_municipal p
                 inner join municipios m on p.id_municipio = m.id_municipio
                 inner join estados e on m.id_uf = e.id_uf
        where (? is NULL or e.id_regiao = ?)
        group by e.nome_uf; \
        """
    rows = query(q, (id_regiao,id_regiao))
    return rows

@router.get("/populacao/top-municipios", response_model=list[Populacao], tags=["análise"])
def top_municipios(limit: int = Query(default=10, le=100)):
    q = """
        select m.nome_municipio as nome, p.valor as total from municipios m
        inner join populacao_municipal p on m.id_municipio=p.id_municipio
        order by total desc
        limit ?
        """
    rows = query(q,(limit,))
    return rows

@router.get("/populacao/distribuicao", response_model=list[Populacao], tags=["análise"])
def distribuicao_populacional():
    q = """
        select m.nome_municipio as nome, p.valor as total from municipios m
        inner join populacao_municipal p
            on p.id_municipio = m.id_municipio
        order by total;
        """
    rows = query(q)
    return rows

@router.get("/populacao/dispersao-uf", response_model=list[Dispersao], tags=["análise"])
def dispersao_por_uf():
    q = """
        select e.id_regiao, e.nome_uf as nome, avg(p.valor) as media, count(p.id_municipio) as quant from populacao_municipal p
            inner join municipios m on p.id_municipio = m.id_municipio
            inner join estados e on m.id_uf = e.id_uf
            group by e.nome_uf
        """
    rows = query(q)
    return rows

@router.get("/populacao/heatmap-regiao-porte", response_model=list[PorteRegiao], tags=["análise"])
def heatmap_regiao_porte():
    q = """
        SELECT r.nome_regiao,
        SUM(CASE
            WHEN p.valor < 70000 THEN 1
            ELSE 0
        END) AS pequeno,
    
        SUM(CASE
            WHEN p.valor >= 70000
             AND p.valor < 600000 THEN 1
            ELSE 0
        END) AS medio,
    
        SUM(CASE
            WHEN p.valor >= 600000 THEN 1
            ELSE 0
        END) AS grande
    
    FROM populacao_municipal p
    
    INNER JOIN municipios m
        ON p.id_municipio = m.id_municipio
    
    INNER JOIN estados e
        ON m.id_uf = e.id_uf
    
    INNER JOIN regioes r
        ON r.id_regiao = e.id_regiao
    
    GROUP BY
        r.id_regiao,
        r.nome_regiao
    
    ORDER BY
        r.id_regiao;
            
        """
    rows = query(q)
    return rows

@router.get("/estatisticas/resumo", response_model=list[MedidasResumo], tags=["análise"])
def resumo_estatistico():
    municipios_totais = query("select count(*) as total_municipios from municipios m")[0]["total_municipios"]
    estados_totais = query("select count(*) as total_estados from estados m")[0]["total_estados"]
    populacao_total = query("select sum(valor) as populacao_total from populacao_municipal p")[0]["populacao_total"]
    ano = query("select max(ano) as ano from populacao_municipal")[0]["ano"]
    maior_municipio = query("select m.nome_municipio from municipios m \
            inner join populacao_municipal p on p.id_municipio = m.id_municipio \
            order by p.valor desc limit 1;")[0]["nome_municipio"]

    return [{"municipios": municipios_totais,
            "estados": estados_totais,
            "populacao_total": populacao_total,
            "ano": ano,
            "maior_municipio": maior_municipio}]


@router.get("/municipios/{id_municipio}", response_model=list[DetalheMunicipio], tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    rows = query("select m.id_municipio, nome_municipio, id_uf, p.valor from municipios m \
                 inner join populacao_municipal p on p.id_municipio = m.id_municipio \
                 where m.id_municipio=?", (id_municipio,))
    if not rows:
        raise HTTPException(status_code=404, detail="Municipio não encontrado")
    return rows

@router.post("/municipios", tags=["dados básicos"], status_code=201)
def criar_municipio(nome: str, estado: str, populacao_inicial: int):
    """
    essa função assume que o estado passado como parâmetro já existe.
    caso contrário, lança uma HTTPException.
    """
    id_uf = query("SELECT id_uf from estados where nome_uf=?", (estado,))
    if not id_uf:
        print(id_uf)
        raise HTTPException(status_code=404, detail="Estado não encontrado")
    try:
        id_uf = id_uf[0]["id_uf"]
        id_municipio = query("SELECT MAX(id_municipio) as id_municipio from municipios")[0]["id_municipio"] + 1
        sql_m = 'INSERT INTO municipios(id_municipio, nome_municipio, id_uf) VALUES (?,?,?)'
        sql_p = 'INSERT INTO populacao_municipal(id_municipio, ano, valor) VALUES (?,?,?)'
        execute(sql_m, (id_municipio, nome, id_uf))
        execute(sql_p, (id_municipio, 2025, populacao_inicial))
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))
    return [{
        "mensagem": "municipio criado com sucesso",
        "id_municipio": id_municipio
    }]


@router.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, nome: str | None = Query(default=None), estado: str | None = Query(default=None), populacao_inicial: int | None = Query(default=None)):
    try:
        if estado:
            id_uf = query('select id_uf from estados where nome_uf=?', (estado,))[0]['id_uf']
            if not id_uf:
                raise HTTPException(status_code=400, detail="Estado não encontrado")
            execute('UPDATE municipios SET id_uf=? where id_municipio=?', params=(id_uf, id_municipio))

        if nome:
            execute('UPDATE municipios SET nome_municipio=? WHERE id_municipio=?', params=(nome,id_municipio))

        if populacao_inicial:
            execute('UPDATE populacao_municipal SET valor=? where id_municipio =?', params=(populacao_inicial, id_municipio))
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))
    return [{
        "mensagem": "Município atualizado com sucesso",
        "id_municipio": id_municipio
    }]


@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):
    try:
        execute('DELETE FROM municipios where id_municipio=?', params=(id_municipio,))
        execute('DELETE FROM populacao_municipal where id_municipio=?', params=(id_municipio,))
    except exception as e:
        raise HTTPException(status_code=501, detail=str(e))
    return [{"mensagem": "município removido com sucesso"}]

# ---------------------------------------------------------------------------
# Cadastro: informações que o gestor registra sobre um município.
#
# Essa tabela não existe no banco original. Antes de implementar as rotas
# abaixo, decidam os campos que fazem sentido (status, prioridade,
# observação, responsável...) e criem a tabela no SQLite.
# ---------------------------------------------------------------------------

"""
CRIAÇÃO DA TABELA REGISTROS COM AS SEGUINTES COLUNAS:
CREATE TABLE registros(
	id_registro INTEGER PRIMARY KEY,
	id_municipio INTEGER,
	observacao TEXT,
	responsavel TEXT,
	FOREIGN KEY(id_municipio) REFERENCES municipios(id_municipio) 
)

"""

@router.post("/municipios/{id_municipio}/registros", tags=["cadastro"])
def criar_registro(id_municipio: int, obs: str, responsavel: str):
    q = ("""
         INSERT INTO registros(id_municipio, observacao, responsavel) VALUES(?,?,?)
         """)
    execute(q, (id_municipio,obs,responsavel))
    return [{"mensagem": "registro criado com sucesso"}]


@router.get("/municipios/{id_municipio}/registros", response_model=list[Registro], tags=["cadastro"])
def listar_registros(id_municipio: int):
    return query('select * from registros where id_municipio=?', (id_municipio,))


@router.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, obs: str | None = None, responsavel: str | None= None):
    if obs:
        a = execute('UPDATE registros SET observacao=? WHERE id_registro=?', (obs, id_registro))
    if responsavel:
        b = execute('UPDATE registros SET responsavel=? where id_registro=?', (responsavel, id_registro))
    if a or b:
        return [{"mensagem": "registro atualizado com sucesso", "id_registro": id_registro}]
    return [{"mensagem": "registro não cadastrado na base"}]

@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    a = execute('DELETE FROM registros WHERE id_registro=?', (id_registro,))
    if a:
        return [{"mensagem": "registro deletado com sucesso", "id_registro": id_registro}]
    return [{"mensagem": "registro não encontrado na base"}]
