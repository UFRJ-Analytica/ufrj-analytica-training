from fastapi import APIRouter, HTTPException, status
from app.database import query, get_connection
from app.schemas import *
from pydantic import BaseModel


## ========= ATENÇAO ============

#O Codigo abaixo assume que a database.db possui uma nova tabela na database, que contém
#as alterações feitas pelo gestor. Como o banco de dados não foi versionado no projeto, para rodar primeiro 
#execute:

'''CREATE TABLE IF NOT EXISTS municipio_registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_municipio INTEGER NOT NULL,
    prioridade TEXT NOT NULL,
    situacao TEXT NOT NULL,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);'''


router = APIRouter(prefix="/rhenan-goncalves", tags=["rhenan_goncalves"])
tabelao = " populacao_municipal natural join (municipios as t left join estados on t.id_uf = estados.id_uf) as k left join regioes on k.id_regiao = regioes.id_regiao "

# === schemas aqui pq se botasse no schemas.py original ia virar bagunça === #

class kpi_rhenan(BaseModel):
    num_muni: int
    num_uf: int
    pop_total: int 
    ano: int 
    top_muni: str

class NomePop_rhenan(BaseModel):
    nome: str
    pop: int

class NomeCount_rhenan(BaseModel):
    nome: str
    count: int

class NomeCountAvg_rhenan(BaseModel):
    nome: str
    count: int
    avg: float
    reg: str

class CriaMuni_rhenan(BaseModel):
    nome_municipio: str
    nome_uf: str
    valor: int

class ConfirmaMuni_rhenan(BaseModel):
    id_municipio: int
    id_uf: int

class Porte_rhenan(BaseModel):
    nome: str
    peq: int
    med: int
    big: int

class AtualizaMuni_rhenan(BaseModel):
    nome_municipio: str | None = None
    nome_uf: str
    valor: int


class Registro_rhenan(BaseModel):
    id: int
    id_municipio: int
    nome_municipio: str | None = None
    prioridade: str
    situacao: str

class CriaRegistro_rhenan(BaseModel):
    id_municipio: int
    prioridade: str
    situacao: str

class AtualizaRegistro_rhenan(BaseModel):
    prioridade: str
    situacao: str

class MuniItem_rhenan(BaseModel):
    id_municipio: int
    nome_municipio: str
    nome_uf: str

class UFItem_rhenan(BaseModel):
    id_uf: int
    nome_uf: str
    sigla_uf: str

# == database helpers == #

def execute(sql: str, params: tuple = ()) -> int:
    # a funcao query fornecida nao persiste mudança na db
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def execute_returning_id(sql: str, params: tuple = ()) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

# == endpoints == #

@router.get("/")
def hello():
    return "omg hiiiiii"

@router.get("/totals", response_model=kpi_rhenan)
def iamstupid():
    text = "SELECT "+ \
    "(SELECT COUNT(*) FROM municipios) AS num_muni, "+\
    "(SELECT COUNT(*) FROM estados) AS num_uf ,"+\
    "(SELECT SUM(valor) FROM populacao_municipal) AS pop_total, "+\
    "(SELECT DISTINCT ano FROM populacao_municipal) AS ano, "+\
    "( "+\
        "SELECT nome_municipio "+\
        "FROM municipios " +\
        "WHERE id_municipio = ( " +\
            "SELECT id_municipio " +\
            "FROM populacao_municipal "+\
            "ORDER BY valor DESC "+\
            "LIMIT 1 "+\
        ") "+\
    ") AS top_muni;"
    k = query(text)
    return k[0]

@router.get("/muni", response_model=list[NomePop_rhenan])
def goretzkaaa(limit: int = -1):
    text = "select nome_municipio as nome, valor as pop from" + tabelao + "order by valor desc"
    params = ()
    if limit < -1:
        raise HTTPException(status_code=400)
    if limit != -1:
        text = "select nome_municipio as nome, valor as pop from raw_municipios_com_populacao order by valor desc limit ?"
        params = (limit,)
    k = query(text, params)
    return k

@router.get("/uf", response_model=list[NomePop_rhenan])
def ankaramessi(regs: str = ""):
    regioes_validas = {r["nome_regiao"] for r in query("SELECT DISTINCT nome_regiao FROM regioes")}
    text_1 = "select nome_uf as nome, sum(valor) as pop from" + tabelao
    text_2 = ""
    text_3 = " group by nome_uf order by pop desc"
    params = ()
    if len(regs) > 0:
        lregs = [r.strip() for r in regs.split(",")]
        invalidas = [r for r in lregs if r not in regioes_validas]
        if invalidas:
            raise HTTPException(status_code=400)
        interrogs = ", ".join(["?"] * len(lregs))
        text_2 = f" where nome_regiao in ({interrogs})"
        params = tuple(lregs)
    k = query(text_1 + text_2 + text_3, params)
    return k

@router.get("/uf/stats", response_model=list[NomeCountAvg_rhenan])
def edenilson41anospipipisubiuabandeira():
    text = "select nome_uf as nome, count(valor) as count, avg(valor) as avg, nome_regiao as reg from" + tabelao + "group by nome_uf order by nome_uf"
    return query(text)

@router.get("/reg", response_model=list[NomePop_rhenan])
def xabloing():
    text = "select nome_regiao nome, sum(valor) as pop from" + tabelao + "group by nome_regiao"
    k = query(text)
    return k

@router.get("/reg/porte", response_model=list[Porte_rhenan])
def elefezdnvumamaquina():
    text = (
        "select nome_regiao as nome, "
        "count(case when valor <= 5e4 then 1 end) as peq, "
        "count(case when valor > 5e4 and valor <= 5e5 then 1 end) as med, "
        "count(case when valor > 5e5 then 1 end) as big "
        "from "
        + tabelao
        + "group by nome_regiao"
    )
    return query(text)

@router.post("/muni", response_model=ConfirmaMuni_rhenan)
def oimpossivelaconteceu(data: CriaMuni_rhenan):
    id_municipio = int(query("select max(id_municipio) as m from municipios")[0]['m']) + 1
    id_uf = query("select id_uf as m from estados where nome_uf = ?", (data.nome_uf,))
    if not id_uf:
        raise HTTPException(400, "Estado não existe")
    id_uf = id_uf[0]['m']
    text = "insert into municipios(id_municipio,nome_municipio,id_uf) values (?, ?, ?)"
    params = (id_municipio, data.nome_municipio, id_uf)
    text2 = "insert into populacao_municipal(id_municipio, ano, valor) values (?, 2025, ?)"
    params2 = (id_municipio, data.valor)
    try:
        execute(text, params)
        execute(text2, params2)
    except Exception:
        raise HTTPException(500, "Erro ao criar município")
    return {"id_municipio": id_municipio, "id_uf": id_uf}

@router.put("/muni/{id_municipio}")
def antigravity_my_beloved(id_municipio: int, data: AtualizaMuni_rhenan):
    municipio = query("SELECT * FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if not municipio:
        raise HTTPException(404, "Município não existe")

    uf = query("SELECT id_uf FROM estados WHERE nome_uf = ?", (data.nome_uf,))
    if not uf:
        raise HTTPException(400, "Estado não existe")

    id_uf = uf[0]["id_uf"]

    try:
        if data.nome_municipio:
            execute(
                "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
                (data.nome_municipio, id_uf, id_municipio)
            )
        else:
            execute(
                "UPDATE municipios SET id_uf = ? WHERE id_municipio = ?",
                (id_uf, id_municipio)
            )

        updated_pop = execute(
            "UPDATE populacao_municipal SET valor = ? WHERE id_municipio = ? AND ano = 2025",
            (data.valor, id_municipio)
        )
        if updated_pop == 0:
            execute(
                "INSERT INTO populacao_municipal (id_municipio, ano, valor) VALUES (?, 2025, ?)",
                (id_municipio, data.valor)
            )

    except Exception as e:
        raise HTTPException(500, f"Erro ao atualizar município: {str(e)}")

    return {
        "id_municipio": id_municipio,
        "id_uf": id_uf
    }


@router.get("/registros", response_model=list[Registro_rhenan])
def listar_registros(id_municipio: int | None = None):
    text = (
        "SELECT r.id, r.id_municipio, m.nome_municipio, r.prioridade, r.situacao "
        "FROM municipio_registros r "
        "LEFT JOIN municipios m ON r.id_municipio = m.id_municipio"
    )
    params = ()
    if id_municipio is not None:
        text += " WHERE r.id_municipio = ?"
        params = tuple([id_municipio])
    text += " ORDER BY r.id DESC"
    return query(text, params)

@router.post("/registros", response_model=Registro_rhenan)
def criar_registro(data: CriaRegistro_rhenan):
    municipio = query("SELECT nome_municipio FROM municipios WHERE id_municipio = ?", (data.id_municipio,))
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não existe")
    
    new_id = execute_returning_id(
        "INSERT INTO municipio_registros (id_municipio, prioridade, situacao) VALUES (?, ?, ?)",
        (data.id_municipio, data.prioridade, data.situacao)
    )
    return {
        "id": new_id,
        "id_municipio": data.id_municipio,
        "nome_municipio": municipio[0]["nome_municipio"],
        "prioridade": data.prioridade,
        "situacao": data.situacao
    }

@router.put("/registros/{id_registro}", response_model=Registro_rhenan)
def atualizar_registro(id_registro: int, data: AtualizaRegistro_rhenan):
    registro = query("SELECT * FROM municipio_registros WHERE id = ?", (id_registro,))
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    
    execute(
        "UPDATE municipio_registros SET prioridade = ?, situacao = ? WHERE id = ?",
        (data.prioridade, data.situacao, id_registro)
    )
    
    updated = query(
        "SELECT r.id, r.id_municipio, m.nome_municipio, r.prioridade, r.situacao "
        "FROM municipio_registros r "
        "LEFT JOIN municipios m ON r.id_municipio = m.id_municipio "
        "WHERE r.id = ?",
        (id_registro,)
    )
    return updated[0]

@router.delete("/registros/{id_registro}")
def deletar_registro(id_registro: int):
    registro = query("SELECT * FROM municipio_registros WHERE id = ?", (id_registro,))
    if not registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    execute("DELETE FROM municipio_registros WHERE id = ?", (id_registro,))
    return {"status": "sucesso", "id": id_registro}

@router.get("/muni-lista", response_model=list[MuniItem_rhenan])
def listar_todos_municipios():
    text = (
        "SELECT m.id_municipio, m.nome_municipio, e.nome_uf "
        "FROM municipios m "
        "JOIN estados e ON m.id_uf = e.id_uf "
        "ORDER BY m.nome_municipio"
    )
    return query(text)

@router.get("/estados-lista", response_model=list[UFItem_rhenan])
def listar_todos_estados():
    text = "SELECT id_uf, nome_uf, sigla_uf FROM estados ORDER BY nome_uf"
    return query(text)
