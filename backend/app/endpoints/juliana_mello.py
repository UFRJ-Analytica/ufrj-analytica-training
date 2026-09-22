from fastapi import APIRouter, Query, HTTPException
from app.database import get_connection, query 
from pydantic import BaseModel
router = APIRouter(prefix="/juliana-mello", tags=["juliana_mello"])

@router.get("/status")
def status():
    return {"status": "ok"}

# modelos pydantic para validação:

class MunicipiosCreate(BaseModel):
    id_municipio: int
    nome_municipio: str
    id_uf: int
    populacao: int

# CRUD de município (dados básicos: nome, estado, população)
@router.post("/municipios")
def criar_municipio(dados: MunicipiosCreate):
    conn = get_connection()
    novo_id_row = conn.execute("SELECT MAX(id_municipio) FROM municipios").fetchone()
    novo_id = (novo_id_row[0] or 0) + 1
    conn.execute(
        "INSERT INTO municipios (id_municipio, nome_municipio, id_uf) VALUES (?, ?, ?)",
        (novo_id, dados.nome_municipio, dados.id_uf)
    )
    conn.execute(
        """INSERT INTO populacao_municipal (id_municipio, ano, indicador, valor, unidade, fonte)
           VALUES (?, 2025, 'populacao_residente_estimada', ?, 'pessoas', 'Cadastro manual - gestor')""",
        (novo_id, dados.populacao)
    )
    conn.commit()
    conn.close()
    return {"id_municipio": novo_id, "mensagem": "Município criado com sucesso!"}


@router.put("/municipios/{id_municipio}")
def atualizar_municipio(id_municipio: int, dados: MunicipiosCreate):
    conn = get_connection()
    existe = conn.execute("SELECT 1 FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado")
    conn.execute(
        "UPDATE municipios SET nome_municipio = ?, id_uf = ? WHERE id_municipio = ?",
        (dados.nome_municipio, dados.id_uf, id_municipio)
    )
    conn.execute(
        """UPDATE populacao_municipal SET valor = ?
           WHERE id_municipio = ? AND indicador = 'populacao_residente_estimada'""",
        (dados.populacao, id_municipio)
    )
    conn.commit()
    conn.close()
    return {"mensagem": "Município atualizado com sucesso!"}


@router.delete("/municipios/{id_municipio}")
def remover_municipio(id_municipio: int):
    conn = get_connection()
    existe = conn.execute("SELECT 1 FROM municipios WHERE id_municipio = ?", (id_municipio,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Município não encontrado")
    conn.execute("DELETE FROM populacao_municipal WHERE id_municipio = ?", (id_municipio,))
    conn.execute("DELETE FROM municipios WHERE id_municipio = ?", (id_municipio,))
    conn.commit()
    conn.close()
    return {"mensagem": "Município removido com sucesso!"}

class RegistroGestorCreate(BaseModel):
    status: str
    prioridade: str
    observacao: str
    responsavel: str

# KPIs
@router.get("/estatisticas/resumo")
def resumo_estatistico():
    sql = """
    SELECT 
        (SELECT COUNT(*) FROM municipios) as total_municipios,
        (SELECT COUNT(DISTINCT id_uf) FROM estados) as total_estados,
        (SELECT SUM(valor) FROM populacao_municipal WHERE indicador = 'populacao_residente_estimada') as populacao_total,
        (SELECT MAX(ano) FROM populacao_municipal WHERE indicador = 'populacao_residente_estimada') as ano_ref,
        (SELECT m.nome_municipio FROM municipios m 
         JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
         WHERE p.indicador = 'populacao_residente_estimada' 
         ORDER BY p.valor DESC LIMIT 1) as municipio_mais_populoso
    """ # usa distintct existem varios municipios em cada estado e o id desses estados seriam contados várias vezes >> isso considerando a query que fez uma linha pra cada municipio
    resultado = query(sql)
    return resultado[0] if resultado else {"message": "Nenhum dado encontrado."}
    # o índice [0] faz retornar apenas o primeiro registro do resultado, que é o resumo estatístico, já que a função query() retorna a lista toda

# top N municípios mais populosos
@router.get("/populacao/top-municipios")
def top_municipios(limit: int = Query(default = 10, le = 100)): # indica uma função  que aceita um parâmetro "limit" e ele tem que ser int
            # esse int é enviado diretamente pela URL 
            # o "Query()" é a ferramenta do FastAPI que serve pra configurar e validar os parâmetros  que passam pela URL
            # "default = 10" indica que se o usuário não digitar nada na URL quando acessar a rota (só abrir /populacao/top-municipios sem passar nenhum número) o valor assumido vai ser 10 (retornando o top 10)
            # 'le = 100" le = less than or equal to. impede que envie um número muuuito grande pra ser o limite, nesse caso, não pode ser maior que 100
    sql = """
    SELECT m.nome_municipio, p.valor AS populacao
    FROM municipios m
    JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
    ORDER BY p.valor DESC
    LIMIT ?
"""
    return query(sql, (limit,))  # passando o parâmetro limit para a query
    # a função query() - que ta em database.py - é responsável por executar a consulta SQL no banco de dados e retornar os resultados. O parâmetro limit é passado como uma tupla (limit,) para garantir que seja tratado corretamente como um valor único na consulta SQL.
    # ou seja, retorna a lista inteira direto p quem chamou a API

# populção por região
@router.get("/populacao/por-regiao")
def populacao_por_regiao():
    sql = """
    SELECT r.nome_regiao, SUM(p.valor) AS populacao_total
    FROM regioes r
    JOIN estados e ON r.id_regiao = e.id_regiao
    JOIN municipios m ON e.id_uf = m.id_uf
    JOIN populacao_municipal p ON m.id_municipio = p.id_municipio
    WHERE p.indicador = 'populacao_residente_estimada'
    GROUP BY r.id_regiao, r.nome_regiao
    """
    return query(sql)  # retorna a lista inteira direto p quem chamou a API

# população por estado (com filtro opicional por região)
@router.get("/populacao/por-uf")
def populacao_por_uf(id_regiao: int = Query(default = None)):
    sql = """
    SELECT e.nome_uf, e.sigla_uf, SUM(p.valor) as populacao_total
    FROM estados e
    JOIN municipios m ON m.id_uf = e.id_uf
    JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
    WHERE p.indicador = 'populacao_residente_estimada'
    """
    parametros = [] # faz uma lista vazia que vai receber os parâmetros da query, caso o usuário passe algum filtro
    if id_regiao is not None: # se o usuário passar um filtro de região
        sql += " AND e.id_regiao = ?" # add a linha que vai filtrar pra aparecer só a região que o usuário colocou como filtro
        parametros.append(id_regiao) # add na lista de parâmetros 
    sql += " GROUP BY e.nome_uf, e.id_uf, e.sigla_uf ORDER BY populacao_total DESC"
    return query(sql, parametros)

# municípios x população média por estado (para o scatter)
@router.get("/populacao/dispersao-uf")
def dispersao_por_uf():
    sql = """
    SELECT e.nome_uf, r.nome_regiao,
           COUNT(m.id_municipio) as qtd_municipios,
           AVG(p.valor) as populacao_media
    FROM estados e
    JOIN regioes r ON e.id_regiao = r.id_regiao
    JOIN municipios m ON m.id_uf = e.id_uf
    JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
    WHERE p.indicador = 'populacao_residente_estimada'
    GROUP BY e.id_uf, e.nome_uf, r.nome_regiao
    """
    return query(sql)

# lista de regiões (id + nome), usado para popular filtros na tela
@router.get("/regioes")
def listar_regioes():
    return query("SELECT id_regiao, nome_regiao FROM regioes")

# distribuição populacional 
@router.get("/populacao/distribuicao")
def distribuicao_populacional():
    sql = """
        SELECT valor FROM populacao_municipal
        WHERE indicador = 'populacao_residente_estimada'
        """  # entrega os numeros brutos para a biblioteca de gráficos montar o histograma
    return query (sql)

# heatmap região x porte do município
@router.get("/populacao/heatmap-porte")
def heatmap_regiao_porte():
    sql = """
    SELECT r.nome_regiao,
        CASE 
            WHEN p.valor < 20000 THEN 'Pequeno'
            WHEN p.valor < 100000 THEN 'Médio'
            ELSE 'Grande'
        END as porte,
        COUNT(*) as quantidade
    FROM regioes r
    JOIN estados e ON r.id_regiao = e.id_regiao
    JOIN municipios m ON m.id_uf = e.id_uf
    JOIN populacao_municipal p ON p.id_municipio = m.id_municipio
    WHERE p.indicador = 'populacao_residente_estimada'
    GROUP BY r.nome_regiao, porte
    """
    return query(sql)

# cadastro de anotação do gestor
def criar_tabela_registros():
    conn = get_connection() # essa função get_conection() é a que ta em database.py e ela cria a conexão com o banco de dados
    conn.execute("""
    CREATE TABLE IF NOT EXISTS registros_gestor(
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_municipio INTEGER,
        status TEXT,
        prioridade TEXT,
        observacao TEXT,
        responsavel TEXT
        )
    """)  # essa tabela vai armazenar os registros do gestor, com o id do municipio, status, prioridade, observação e responsável
    conn.commit() # essa linha é necessária para salvar as alterações no banco de dados, garantindo que a tabela seja criada de fato
    conn.close() # fecha a conexão com o banco de dados, liberando recursos e evitando possíveis problemas de conexão futura

criar_tabela_registros() # chama a função que cria a tabela de registros do gestor, caso ela não exista


@router.post("/municipios/{id_municipio}/registros") # essa rota vai permitir que o usuário crie um registro de anotação do gestor para um município específico, identificado pelo id_municipio
def criar_registro(id_municipio: int, dados: RegistroGestorCreate): # essa função vai receber o id do município e os dados do registro (status, prioridade, observação e responsável) que serão validados pelo modelo RegistroGestorCreate
    conn = get_connection()
    cursor = conn.execute( """
    INSERT INTO registros_gestor (id_municipio, status, prioridade, observacao, responsavel)
    VALUES(?, ?, ?, ?, ?) """, # essa linha executa a query SQL para inserir os dados do registro na tabela registros_gestor, usando os valores fornecidos pelo usuário
    (id_municipio, dados.status, dados.prioridade, dados.observacao, dados.responsavel)) # essa tupla contém os valores que serão inseridos na tabela, correspondendo aos campos definidos na query SQL
    conn.commit()
    novo_id = cursor.lastrowid  # obtém o ID do registro recém-criado
    conn.close()
    return {"id_registro": novo_id, "mensagem": "Registro criado com sucesso!!"}

@router.get("/municipios/{id_municipio}/registros") # essa rota vai permitir que o usuário consulte os registros de anotação do gestor para um município específico, identificado pelo id_municipio
def listar_registros(id_municipio: int):
    return query("SELECT * FROM registros_gestor WHERE id_municipio = ?", (id_municipio,)) # essa linha executa a query SQL para selecionar todos os registros da tabela registros_gestor que correspondem ao id do município fornecido pelo usuário, retornando os resultados como uma lista de dicionários

@router.put("/registros/{id_registro}")
def editar_registro(id_registro: int, dados: RegistroGestorCreate):
    conn = get_connection()
    existe = conn.execute("SELECT 1 FROM registros_gestor WHERE id_registro = ?", (id_registro,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    conn.execute(
        """UPDATE registros_gestor 
           SET status = ?, prioridade = ?, observacao = ?, responsavel = ?
           WHERE id_registro = ?""",
        (dados.status, dados.prioridade, dados.observacao, dados.responsavel, id_registro)
    )
    conn.commit()
    conn.close()
    return {"mensagem": "Registro atualizado com sucesso!"}


@router.delete("/registros/{id_registro}")
def remover_registro(id_registro: int):
    conn = get_connection()
    existe = conn.execute("SELECT 1 FROM registros_gestor WHERE id_registro = ?", (id_registro,)).fetchone()
    if not existe:
        conn.close()
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    conn.execute("DELETE FROM registros_gestor WHERE id_registro = ?", (id_registro,))
    conn.commit()
    conn.close()
    return {"mensagem": "Registro removido com sucesso!"}

