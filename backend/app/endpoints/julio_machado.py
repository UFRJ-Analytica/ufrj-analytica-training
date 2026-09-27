from fastapi import APIRouter, FastAPI, HTTPException, Query
from app.database import query, get_connection
from pydantic import BaseModel

router = APIRouter(prefix="/julio_machado", tags=["julio_machado"])

#Schema do pydantic 
class Estado(BaseModel):
    id_uf: int
    sigla_uf: str
    nome_uf: str


class Municipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int


class Pop_municipio(BaseModel):
    id_municipio: int
    nome_municipio: str
    populacao: int
    unidade: str


class Pop_regiao(BaseModel):
    nome_regiao: str
    populacao: int
    unidade: str


class Pop_estado(BaseModel):
    id_uf: int
    nome_uf: str
    sigla_uf: str
    populacao: int
    unidade: str


class Dist_pop(BaseModel):
    PEQUENO: int
    MEDIO: int
    GRANDE: int


class Disp_estado(BaseModel):
    nome_regiao: str
    sigla_uf: str
    total_municipios: int
    populacao_media: float


class Heat_regiao(BaseModel):
    id_regiao: int
    nome_regiao: str
    PEQUENO: int
    MEDIO: int
    GRANDE: int
    total_municipios: int


class KPIs(BaseModel):
    total_municipios: int
    total_estados: int
    populacao_total_brasil: int
    ano_referencia: int
    municipio_mais_populoso: str


class Compl_municipio(BaseModel):
    id_regiao: int | None
    nome_regiao: str | None
    sigla_regiao: str | None
    id_uf: int
    nome_uf: str | None
    sigla_uf: str | None
    id_municipio: int
    nome_municipio: str
    valor: int | None
    unidade: str | None
    id_censo: int | None
    ano: int | None
    fonte: str | None

class MunicipioCreate(BaseModel):
    nome_municipio: str
    id_uf: int
    valor: int
    unidade: str

class MunicipioUpdate(BaseModel):
    nome_municipio: str | None = None
    id_uf: int | None = None
    valor: int | None = None
    unidade: str | None = None

class RegistroCreate(BaseModel):
    status: str
    prioridade: int
    descricao: str


class RegistroUpdate(BaseModel):
    id_municipio: int | None = None
    status: str | None = None
    prioridade: int | None = None
    descricao: str | None = None


class Registro(BaseModel):
    id_registro: int
    id_municipio: int
    status: str
    prioridade: int
    descricao: str


@router.get("/status")
def status():
    return {"status": "ok"}


@router.get("/estados",response_model=list[Estado], tags=["dados básicos"])
def listar_estados(id_regiao: int | None = Query(default=None)):
    rows = query("""
        SELECT 
            e.id_uf, 
            e.sigla_uf, 
            e.nome_uf
        FROM estados e
        WHERE (? IS NULL OR id_regiao = ?)
        ORDER BY id_uf
    """, (id_regiao, id_regiao))
    return rows

@router.get("/municipios", response_model=list[Municipio], tags=["dados básicos"])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    rows = query("""
        SELECT 
            m.id_municipio, 
            m.nome_municipio, 
            m.id_uf
        FROM municipios m
        WHERE (? IS NULL OR nome_municipio LIKE '%' || ? || '%')
        AND (? IS NULL OR id_uf = ?)
        LIMIT ?
    """, (nome, nome, id_uf, id_uf, limit))
    return rows

@router.get("/populacao/top-municipios", response_model=list[Pop_municipio], tags=["análise"])
def top_municipios(limit: int = Query(default=10, ge=1, le=100)):
    rows = query("""
        SELECT 
            m.id_municipio, 
            m.nome_municipio, 
            r2.valor as populacao, 
            r2.unidade
        FROM municipios m
        INNER JOIN recenseamento r2
            ON m.id_municipio = r2.id_municipio AND r2.id_censo = 1
        ORDER BY populacao DESC
        LIMIT ?
    """, (limit,))
    return rows

@router.get("/populacao/por-regiao", response_model=list[Pop_regiao], tags=["análise"])
def populacao_por_regiao():
    rows = query("""
        SELECT 
            r.id_regiao, 
            r.nome_regiao, 
            r.sigla_regiao, 
            SUM(r2.valor) as populacao, 
            r2.unidade
        FROM regioes r
        INNER JOIN estados e
            ON r.id_regiao = e.id_regiao
        INNER JOIN municipios m
                ON e.id_uf = m.id_uf
        INNER JOIN recenseamento r2
            ON m.id_municipio = r2.id_municipio AND r2.id_censo = 1
        GROUP BY r.nome_regiao
    """)
    return rows


@router.get("/populacao/por-uf", response_model=list[Pop_estado], tags=["análise"])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    rows = query("""
            SELECT 
                e.id_uf,
                e.nome_uf, 
                e.sigla_uf, 
                SUM(r2.valor) as populacao, 
                r2.unidade
            FROM municipios m
            INNER JOIN estados e
	            ON m.id_uf = e.id_uf
            INNER JOIN recenseamento r2
	            ON m.id_municipio = r2.id_municipio
            WHERE (? IS NULL OR e.id_regiao = ?)
            GROUP BY e.nome_uf, e.id_uf, e.sigla_uf
            ORDER BY populacao DESC
        """, (id_regiao, id_regiao))
    return rows


@router.get("/populacao/distribuicao",  response_model=list[Dist_pop], tags=["análise"])
def distribuicao_populacional():
    rows = query("""
                SELECT
	                SUM(IF(r2.valor < 100000, 1, 0)) AS PEQUENO,
	                COUNT(CASE WHEN r2.valor >= 100000 AND valor < 500000 THEN 1 END) AS MEDIO,
	                COUNT(r2.valor) FILTER(WHERE valor >= 500000) AS GRANDE
                FROM municipios m 
                INNER JOIN recenseamento r2 
	                ON m.id_municipio = r2.id_municipio AND r2.id_censo = 1
            """)
    return rows


@router.get("/populacao/dispersao-uf", response_model=list[Disp_estado], tags=["análise"])
def dispersao_por_uf():
    rows = query("""
        SELECT 
            r.nome_regiao,
            e.sigla_uf,
            COUNT(m.id_municipio) AS total_municipios,
            ROUND(AVG(r2.valor), 0) AS populacao_media
        FROM estados e
        INNER JOIN municipios m 
            ON e.id_uf = m.id_uf
        INNER JOIN recenseamento r2
            ON m.id_municipio = r2.id_municipio
        INNER JOIN regioes r
            ON e.id_regiao = r.id_regiao
        GROUP BY e.sigla_uf, r.nome_regiao
    """)

    return rows


@router.get("/populacao/heatmap-regiao-porte", response_model=list[Heat_regiao], tags=["análise"])
def heatmap_regiao_porte():
    rows = query("""
                SELECT
                    r.id_regiao, r.nome_regiao,
	                SUM(IF(r2.valor < 100000, 1, 0)) AS PEQUENO,
	                COUNT(CASE WHEN r2.valor >= 100000 AND r2.valor < 500000 THEN 1 END) AS MEDIO,
	                COUNT(r2.valor) FILTER(WHERE r2.valor >= 500000) AS GRANDE,
                    COUNT(m.id_municipio) AS total_municipios
                FROM municipios m
                INNER JOIN recenseamento r2
	                ON m.id_municipio = r2.id_municipio AND r2.id_censo = 1
                INNER JOIN estados e
                    ON m.id_uf = e.id_uf
                INNER JOIN regioes r
                    ON e.id_regiao = r.id_regiao
                GROUP BY r.id_regiao, r.nome_regiao
            """)
    return rows


@router.get("/estatisticas/resumo", tags=["análise"])
def resumo_estatistico():
    rows = query("""
            SELECT 
                (SELECT COUNT(m.id_municipio) FROM municipios m) AS total_municipios,
                (SELECT COUNT(e.id_uf) FROM estados e) AS total_estados,
                (SELECT SUM(r2.valor) FROM recenseamento r2) AS populacao_total_brasil,
                (SELECT c.ano FROM censos c WHERE c.id_censo = 1) AS ano_referencia,
                (
                    SELECT 
                        m.nome_municipio
                    FROM municipios m
                    INNER JOIN recenseamento r2
                        ON m.id_municipio = r2.id_municipio
                    ORDER BY r2.valor DESC
                    LIMIT 1
                ) AS municipio_mais_populoso
    """)
    return rows


@router.get("/municipios/{id_municipio}", response_model=list[Compl_municipio], tags=["dados básicos"])
def detalhe_municipio(id_municipio: int):
    rows = query("""
            SELECT 
                r.id_regiao,
                r.nome_regiao,
                r.sigla_regiao,
                m.id_uf,
                e.nome_uf,
                e.sigla_uf,
                m.id_municipio,
                m.nome_municipio,
                r2.valor,
                r2.unidade,
                c.id_censo,
                c.ano,
                c.fonte
            FROM municipios m
            LEFT JOIN estados e
                ON m.id_uf = e.id_uf
            LEFT JOIN regioes r
                ON e.id_regiao = r.id_regiao
            LEFT JOIN recenseamento r2
                ON m.id_municipio = r2.id_municipio
            LEFT JOIN censos c
                ON r2.id_censo = c.id_censo
            WHERE m.id_municipio = ?

    """, (id_municipio,))
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Município não encontrado.",
        )
    return rows


@router.post("/municipios", tags=["dados básicos"])
def criar_municipio(municipio: MunicipioCreate):

    conn = get_connection()
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO municipios(id_municipio, nome_municipio, id_uf)
            VALUES ((SELECT MAX(id_municipio) + 1 FROM municipios), ?, ?)
        """, (municipio.nome_municipio, municipio.id_uf))

        cursor.execute("""
            INSERT INTO recenseamento(id_municipio, valor, unidade)
            VALUES((SELECT MAX(id_municipio) FROM municipios), ?, ?)
        """, (municipio.valor, municipio.unidade))
        conn.commit()
        cursor.execute("""
            SELECT 
                m.id_municipio,
                m.nome_municipio,
                m.id_uf,
                r2.valor,
                r2.unidade
            FROM municipios m
            INNER JOIN recenseamento r2 
                ON m.id_municipio = r2.id_municipio 
            WHERE m.id_municipio = (SELECT MAX(id_municipio) FROM municipios)
        """)
        mun = cursor.fetchone()
        return dict(mun)
        
    finally:
        conn.close()



@router.put("/municipios/{id_municipio}", tags=["dados básicos"])
def atualizar_municipio(id_municipio: int, municipio: MunicipioUpdate):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Município não encontrado")
        
        cursor.execute("""
            UPDATE municipios 
            SET nome_municipio = ?, id_uf = ?
            WHERE id_municipio = ?
        """, (municipio.nome_municipio, municipio.id_uf, id_municipio))
        cursor.execute("""
            UPDATE recenseamento 
            SET valor = ?, unidade = ?
            WHERE id_municipio = ?
        """, (municipio.valor, municipio.unidade, id_municipio))
        conn.commit()
        cursor.execute("""
            SELECT 
                m.id_municipio,
                m.nome_municipio,
                m.id_uf,
                r2.valor,
                r2.unidade
            FROM municipios m
            INNER JOIN recenseamento r2 
                ON m.id_municipio = r2.id_municipio 
            WHERE m.id_municipio = ?
        """, (id_municipio,))
        
        mun = cursor.fetchone()
        return dict(mun)
        
    finally:
        conn.close()


@router.delete("/municipios/{id_municipio}", tags=["dados básicos"])
def remover_municipio(id_municipio: int):

    conn = get_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
        mun = cursor.fetchone()
        
        if mun is None:
            raise HTTPException(status_code=404, detail="Município não encontrado")
        
        cursor.execute("DELETE FROM recenseamento WHERE id_municipio = ?", (id_municipio,))
        cursor.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
        conn.commit()
        return HTTPException(status_code=204, detail="Município deletado com sucesso.")
        
    finally:
        conn.close()

    
## Cria tabela de registros
query("""
    CREATE TABLE IF NOT EXISTS registros (
        id_registro INTEGER PRIMARY KEY,
        id_municipio INTEGER NOT NULL,
        status TEXT NOT NULL,
        prioridade INT NOT NULL,
        descricao TEXT NOT NULL,
        FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
    );
""")

@router.post(
    "/municipios/{id_municipio}/registros",
    response_model= RegistroCreate,
    tags=["cadastro"]
)
def criar_registro(id_municipio: int, registro: RegistroCreate):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Município não encontrado")
        
        cursor.execute("""
            INSERT INTO registros (id_municipio, status, prioridade, descricao)
            VALUES (?, ?, ?, ?)
        """, (id_municipio, registro.status, registro.prioridade, registro.descricao))
        
        conn.commit()
        
        cursor.execute("""
            SELECT id_registro, id_municipio, status, prioridade, descricao
            FROM registros
            WHERE id_registro = (SELECT MAX(id_registro) FROM registros)
        """)
        return dict(cursor.fetchone())
    finally:
        conn.close()


@router.get(
    "/municipios/{id_municipio}/registros",
    response_model=list[Registro],
    tags=["cadastro"]
)
def listar_registros(id_municipio: int):
    mun = query("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (id_municipio,))
    if mun is None:
        raise HTTPException(status_code=404, detail="Município não encontrado.")

    rows = query("""SELECT * 
                    FROM registros 
                    WHERE id_municipio = ?
                    ORDER BY id_registro DESC""", (id_municipio,))
    return rows


@router.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, registro: RegistroUpdate):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_registro FROM registros WHERE id_registro = ?", (id_registro,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        
        if registro.id_municipio is not None:
            cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ?", (registro.id_municipio,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Município não encontrado")

        cursor.execute("""
            UPDATE registros 
            SET id_municipio = COALESCE(?, id_municipio), 
                status = COALESCE(?, status), 
                prioridade = COALESCE(?, prioridade), 
                descricao = COALESCE(?, descricao)
            WHERE id_registro = ?
        """, (registro.id_municipio, registro.status, registro.prioridade, registro.descricao, id_registro))
        
        conn.commit()
        
        cursor.execute("""
            SELECT id_registro, id_municipio, status, prioridade, descricao
            FROM registros
            WHERE id_registro = ?
        """, (id_registro,))

        return dict(cursor.fetchone())
    
    finally:
        conn.close()


@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_registro FROM registros WHERE id_registro = ?", (id_registro,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        
        cursor.execute("DELETE FROM registros WHERE id_registro = ?", (id_registro,))
        conn.commit()
        
        return HTTPException(status_code=204, detail="Registro deletado com sucesso.")
    
    finally:
        conn.close()
    
