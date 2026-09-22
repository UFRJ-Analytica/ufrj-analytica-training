from fastapi import APIRouter, Query, HTTPException
from app.database import query, get_connection
from app import schemas

router = APIRouter(prefix="/felipe-indio", tags=["felipe_indio"])

def criar_tabela_registros():
    """Cria a tabela de registros locais do gestor se não existir."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                id_municipio INTEGER NOT NULL,
                status TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                observacao TEXT,
                responsavel TEXT NOT NULL,
                FOREIGN KEY(id_municipio) REFERENCES municipios(id_municipio)
            )
        """)
        conn.commit()
    finally:
        conn.close()
criar_tabela_registros()

@router.get("/status")
def status():
    return {"status": "ok"}

@router.get("/estados")
def listar_estados(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT
            id_uf,
            sigla_uf,
            nome_uf,
            id_regiao
        FROM estados
    """
    params = ()
    if id_regiao is not None:
        sql += " WHERE id_regiao = ?"
        params = (id_regiao,)

    sql += " ORDER BY nome_uf"
    return query(sql, params)

@router.get("/estatisticas/resumo", response_model=schemas.ResumoEstatistico)
def resumo_estatistico():
    total_municipios = query("SELECT COUNT(*) as c FROM municipios")[0]['c']
    total_estados = query("SELECT COUNT(*) as c FROM estados")[0]['c']
    populacao_total = query("SELECT SUM(valor) as s FROM populacao_municipal")[0]['s']
    ano_referencia = query("SELECT MAX(ano) as m FROM populacao_municipal")[0]['m']
    mais_populoso = query("""
        SELECT m.nome_municipio 
        FROM populacao_municipal p 
        JOIN municipios m ON p.id_municipio = m.id_municipio 
        ORDER BY p.valor DESC LIMIT 1
    """)[0]['nome_municipio']
    return {
        "total_municipios": total_municipios,
        "total_estados": total_estados,
        "populacao_total": populacao_total,
        "ano_referencia": ano_referencia,
        "municipio_mais_populoso": mais_populoso
    }

@router.get("/populacao/top-municipios", response_model=list[schemas.TopMunicipio])
def top_municipios(limit: int = Query(default=10, le=100)):
    sql = """
        SELECT m.nome_municipio, e.sigla_uf, p.valor as populacao 
        FROM municipios m 
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        ORDER BY p.valor DESC LIMIT ?
    """
    return query(sql, (limit,))

@router.get("/populacao/por-regiao", response_model=list[schemas.PopulacaoRegiao])
def populacao_por_regiao():
    sql = """
        SELECT r.nome_regiao, SUM(p.valor) as populacao_total 
        FROM populacao_municipal p 
        JOIN municipios m ON p.id_municipio = m.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
        JOIN regioes r ON e.id_regiao = r.id_regiao 
        GROUP BY r.nome_regiao
        ORDER BY populacao_total DESC
    """
    return query(sql)

@router.get("/populacao/por-uf", response_model=list[schemas.PopulacaoUF])
def populacao_por_uf(id_regiao: int | None = Query(default=None)):
    sql = """
        SELECT e.sigla_uf, SUM(p.valor) as populacao_total 
        FROM populacao_municipal p 
        JOIN municipios m ON p.id_municipio = m.id_municipio 
        JOIN estados e ON m.id_uf = e.id_uf 
    """
    params = []
    if id_regiao is not None:
        sql += " WHERE e.id_regiao = ? "
        params.append(id_regiao)
        
    sql += " GROUP BY e.sigla_uf ORDER BY populacao_total DESC"
    return query(sql, tuple(params))

@router.get("/populacao/distribuicao", response_model=list[schemas.DistribuicaoPopulacao])
def distribuicao_populacional():
    sql = """
        SELECT m.nome_municipio, p.valor as populacao 
        FROM populacao_municipal p 
        JOIN municipios m ON p.id_municipio = m.id_municipio
    """
    return query(sql)

@router.get("/populacao/dispersao-uf", response_model=list[schemas.DispersaoUF])
def dispersao_por_uf():
    sql = """
        SELECT 
            e.sigla_uf, 
            e.id_regiao, 
            COUNT(m.id_municipio) as qtd_municipios, 
            AVG(p.valor) as media_populacao 
        FROM estados e 
        JOIN municipios m ON e.id_uf = m.id_uf 
        JOIN populacao_municipal p ON m.id_municipio = p.id_municipio 
        GROUP BY e.sigla_uf, e.id_regiao
    """
    return query(sql)

@router.get("/populacao/heatmap-regiao-porte", response_model=list[schemas.HeatmapPorte])
def heatmap_regiao_porte():
    sql = """
        SELECT 
            r.nome_regiao,
            CASE 
                WHEN p.valor <= 20000 THEN 'Pequeno'
                WHEN p.valor <= 100000 THEN 'Médio'
                ELSE 'Grande'
            END as porte,
            COUNT(m.id_municipio) as quantidade
        FROM populacao_municipal p
        JOIN municipios m ON p.id_municipio = m.id_municipio
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        GROUP BY r.nome_regiao, porte
    """
    return query(sql)

#CRUD Municípios

@router.get("/municipios", response_model=list[schemas.Municipio])
def listar_municipios(
    nome: str | None = Query(default=None),
    id_uf: int | None = Query(default=None),
    limit: int = Query(default=50, le=500),
):
    sql = "SELECT id_municipio, nome_municipio, id_uf FROM municipios WHERE 1=1"
    params = []
    
    if nome:
        sql += " AND nome_municipio LIKE ?"
        params.append(f"%{nome}%")
    if id_uf:
        sql += " AND id_uf = ?"
        params.append(id_uf)
        
    sql += " ORDER BY nome_municipio LIMIT ?"
    params.append(limit)
    
    return query(sql, tuple(params))

@router.get("/municipios/{id_municipio}", response_model=schemas.DetalheMunicipio)
def detalhe_municipio(id_municipio: int):
    sql = """
        SELECT m.id_municipio, m.nome_municipio, e.sigla_uf, r.nome_regiao, p.valor as populacao, p.ano as ano_referencia
        FROM municipios m
        JOIN estados e ON m.id_uf = e.id_uf
        JOIN regioes r ON e.id_regiao = r.id_regiao
        LEFT JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
        WHERE m.id_municipio = ?
    """
    res = query(sql, (id_municipio,))
    if not res:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return res[0]

@router.post("/municipios", response_model=schemas.Municipio, status_code=201)
def criar_municipio(dados: schemas.MunicipioCreate):
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT MAX(id_municipio) as max_id FROM municipios")
        max_id = cursor.fetchone()['max_id'] or 0
        novo_id = max_id + 1

        conn.execute(
            "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
            (novo_id, dados.nome_municipio, dados.id_uf)
        )
        conn.execute(
            "INSERT INTO populacao_municipal (id_municipio, ano, valor, indicador, unidade, fonte) VALUES (?, ?, ?, ?, ?, ?)",
            (novo_id, 2025, dados.populacao_inicial, 'populacao_residente_estimada', 'pessoas', 'SISTEMA_GESTOR')
        )
        conn.commit()
        return {"id_municipio": novo_id, "nome_municipio": dados.nome_municipio, "id_uf": dados.id_uf}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int, dados: schemas.MunicipioUpdate):
    conn = get_connection()
    try:
        if dados.nome_municipio or dados.id_uf:
            updates = []
            params = []
            if dados.nome_municipio:
                updates.append("nome_municipio = ?")
                params.append(dados.nome_municipio)
            if dados.id_uf:
                updates.append("id_uf = ?")
                params.append(dados.id_uf)
            
            sql = f"UPDATE municipios SET {', '.join(updates)} WHERE id_municipio = ?"
            params.append(id_municipio)
            conn.execute(sql, tuple(params))

        if dados.populacao is not None:
            conn.execute(
                "UPDATE populacao_municipal SET valor = ? WHERE id_municipio = ?",
                (dados.populacao, id_municipio)
            )
            
        conn.commit()
        return {"mensagem": "Município atualizado com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM registros WHERE id_municipio = ?", (id_municipio,))
        conn.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
        conn.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
        conn.commit()
        return {"mensagem": "Município e dados dependentes removidos com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.post("/municipios/{id_municipio}/registros", response_model=schemas.Registro, tags=["cadastro"], status_code=201)
def criar_registro(id_municipio: int, dados: schemas.RegistroCreate):
    conn = get_connection()
    try:
        if not conn.execute("SELECT 1 FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone():
            raise HTTPException(status_code=404, detail="Município não encontrado")

        cursor = conn.execute(
            "INSERT INTO registros (id_municipio, status, prioridade, observacao, responsavel) VALUES (?, ?, ?, ?, ?)",
            (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return {**dados.model_dump(), "id_registro": novo_id, "id_municipio": id_municipio}
    finally:
        conn.close()

@router.get("/municipios/{id_municipio}/registros", response_model=list[schemas.Registro], tags=["cadastro"])
def listar_registros(id_municipio: int):
    return query("SELECT * FROM registros WHERE id_municipio = ?", (id_municipio,))

@router.put("/registros/{id_registro}", tags=["cadastro"])
def atualizar_registro(id_registro: int, dados: schemas.RegistroUpdate):
    conn = get_connection()
    try:
        updates = []
        params = []
        for field, value in dados.model_dump(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            params.append(value)
            
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização")
            
        params.append(id_registro)
        sql = f"UPDATE registros SET {', '.join(updates)} WHERE id_registro = ?"
        
        cursor = conn.execute(sql, tuple(params))
        if cursor.rowcount == 0:
             raise HTTPException(status_code=404, detail="Registro não encontrado")
        conn.commit()
        return {"mensagem": "Registro atualizado com sucesso"}
    finally:
        conn.close()

@router.delete("/registros/{id_registro}", tags=["cadastro"])
def remover_registro(id_registro: int):
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM registros WHERE id_registro = ?", (id_registro,))
        if cursor.rowcount == 0:
             raise HTTPException(status_code=404, detail="Registro não encontrado")
        conn.commit()
        return {"mensagem": "Registro removido com sucesso"}
    finally:
        conn.close()