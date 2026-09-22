"""Endpoints separados por trainee.

Cada trainee deve criar seu proprio arquivo nesta pasta, por exemplo:
app/endpoints/nome_sobrenome.py.

O app principal importa automaticamente arquivos que exponham uma variavel
router ou app.
"""

from app.database import get_connection
from fastapi import APIRouter, HTTPException



# router: recebe pedido e sabe pra onde enviar: "Se alguém pedir GET /rebecca_simao/teste, execute a função teste()."
router = APIRouter(prefix="/rebecca_simao", tags=["reb_simao"]) #prefixo: http://127.0.0.1:8000/rebecca_simao/teste


'''@router.get("/teste")
def teste():
    conn = get_connection()  
    cursor = conn.cursor()    
    #faz consultas
    conn.close()
    return { "status": "vem tranquilo🤙"}


chega uma requisição-->abre a conexão-->faz a consulta-->fecha a conexão-->devolve a resposta.  
'''




@router.get("/kpi") #Key Performance Indicator (numeros resumos)
def resumo():
    conn = get_connection()  #conecta com banco
    cursor = conn.cursor()   #conversa com banco

    cursor.execute("SELECT COUNT(*) AS total_regioes FROM regioes;")
    total_regioes = cursor.fetchone()["total_regioes"] # entrega um dicio: total_regioes: num. Quero num. faco retornar[total_regioes]
    
    cursor.execute("SELECT COUNT(*) AS total_municipios FROM municipios;") # Envia consulta pro banco executar
    total_municipios = cursor.fetchone()["total_municipios"] #fetchall guarda varias linhas de resposta (fetchone() guarda uma só)

    cursor.execute("SELECT COUNT(*) AS total_estados FROM estados;")
    total_estados = cursor.fetchone()["total_estados"] 

    cursor.execute("SELECT SUM(valor) AS total_popu FROM populacao_municipal;")
    total_popu = cursor.fetchone()["total_popu"] 

    
    cursor.execute("""SELECT muni.nome_municipio,popu.valor
                FROM populacao_municipal popu
                JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                ORDER BY popu.valor DESC
                LIMIT 1;""")
    muni_mais_popu = cursor.fetchone() 
    
    cursor.execute("SELECT DISTINCT ano FROM populacao_municipal;")
    ano = cursor.fetchone()["ano"] 

    cursor.execute("SELECT DISTINCT fonte FROM populacao_municipal;")
    fonte = cursor.fetchone()["fonte"]

    conn.close()
    return {"total_municipios": total_municipios,"total_estados": total_estados,"municipio mais populoso": muni_mais_popu,
            "total_regioes":total_regioes, "total_populacao": total_popu,"fonte":fonte, "ano": ano}




@router.get("/ranking_popu_muni") 
def ranking_popu_muni(quant:int=3):
    conn = get_connection()  
    cursor = conn.cursor()   
    cursor.execute("""SELECT muni.nome_municipio,popu.valor
                    FROM populacao_municipal popu
                    JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                    ORDER BY popu.valor DESC
                    LIMIT ?;""", (quant,))
    top_muni = cursor.fetchall()
    conn.close()
    return {"Top municipio":top_muni}


@router.get("/popu_regiao") 
def popu_regiao(quant:int=5):
    conn = get_connection()  
    cursor = conn.cursor()   
    cursor.execute("""SELECT regioes.nome_regiao,SUM(popu.valor)
                    FROM populacao_municipal popu
                    JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                    JOIN estados ON muni.id_uf = estados.id_uf 
                    JOIN regioes ON regioes.id_regiao = estados.id_regiao
                    GROUP BY regioes.nome_regiao
                    ORDER BY SUM(popu.valor) DESC
                    LIMIT ?;""", (quant,))
    top_regiao = cursor.fetchall()
    conn.close()
    return {"Top regiao":top_regiao}


#fiz um filtro opcional e mesclei com um ranking
@router.get("/popu_estados")
def popu_estados(nome_regiao: str | None = None, quant: int = 30):
    conn = get_connection()
    cursor = conn.cursor()

    if nome_regiao is None:cursor.execute("""SELECT estados.nome_uf, SUM(popu.valor)
                        FROM populacao_municipal popu
                        JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                        JOIN estados ON muni.id_uf = estados.id_uf
                        GROUP BY estados.nome_uf
                        ORDER BY SUM(popu.valor) DESC
                        LIMIT ?;""",(quant,))

    else:cursor.execute("""SELECT estados.nome_uf, SUM(popu.valor)
                        FROM populacao_municipal popu
                        JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                        JOIN estados ON muni.id_uf = estados.id_uf
                        JOIN regioes ON estados.id_regiao = regioes.id_regiao
                        WHERE regioes.nome_regiao = ?
                        GROUP BY estados.nome_uf
                        ORDER BY SUM(popu.valor) DESC
                        LIMIT ?;""", (nome_regiao, quant))

    resultado = cursor.fetchall()
    conn.close()
    return {"Estados": resultado}



@router.get("/distribuicao_populacao")
def distribuicao():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT valor
                      FROM populacao_municipal;""")
    populacao = cursor.fetchall()
    conn.close()
    return populacao



# se fosse desenhar na mao eu precisaria do nome do estado, qnt de municipios e populacao media (e regiao pra colorir)
# coluna que select que nao t dentro de sum, avg, count, min, max, deve aparecer em group by
@router.get("/dispersao")
def dispersao():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT estados.nome_uf,COUNT(muni.id_municipio) as qntMunicipios, regioes.nome_regiao,AVG(popu.valor) AS popu_media
                    FROM populacao_municipal popu
                    JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                    JOIN estados ON muni.id_uf = estados.id_uf
                    JOIN regioes ON estados.id_regiao = regioes.id_regiao 
                    GROUP BY  estados.nome_uf,regioes.nome_regiao
                    ORDER BY estados.nome_uf;""")
    resultado = cursor.fetchall()
    conn.close()
    return resultado

@router.get("/municipios")
def listar_municipios():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""SELECT muni.id_municipio,muni.nome_municipio,est.id_uf,est.nome_uf
                    FROM municipios muni
                    JOIN estados est  ON muni.id_uf=est.id_uf
                    ORDER BY muni.nome_municipio""")
    resultado=cursor.fetchall()
    conn.close()
    return resultado

# regiao, porte do municipio (peq, medio, grande), qnt municipios
#GROUP BY  regioes.nome_regiao, porte: Sudeste + Grande = 3 por ex // GROUP BY ano, mes (crie grupo de cada mes de cada ano)
@router.get("/heatMap")
def heatMap():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT regioes.nome_regiao,COUNT(muni.id_municipio) as qntMunicipios,
                            CASE WHEN popu.valor < 30000 THEN 'Pequeno'
                                WHEN popu.valor <= 150000 THEN 'Medio'
                                ELSE 'Grande' END AS porte
                            FROM populacao_municipal popu
                            JOIN municipios muni ON popu.id_municipio = muni.id_municipio
                            JOIN estados ON muni.id_uf = estados.id_uf
                            JOIN regioes ON estados.id_regiao = regioes.id_regiao 
                            GROUP BY  regioes.nome_regiao, porte 
                            ORDER BY regioes.nome_regiao, porte """)

    resultado = cursor.fetchall()
    conn.close()
    return resultado


# HTTP: GET DELETE POST PUT (real) -- implementa --> CRUD: CREATE READ UPDATE DELETE (ideia)
# Etapa 2 de alterar os dados do database.db add municipios. altera municipios e população_municipal
def verificar_municipio(cursor, id_municipio):
    cursor.execute("""SELECT id_municipio  FROM municipios  
                    WHERE id_municipio = ?;""", (id_municipio,))
    municipio = cursor.fetchone()
    if municipio is None:
        raise HTTPException(status_code=404,detail="Município não encontrado")


@router.post("/municipios/ibge")
def criar_registro_IBGE(nome_municipio:str,id_uf:int,ano:int,indicador:str,valor:int,unidade:str|None=None,fonte:str|None=None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT id_municipio
                  FROM municipios
                  WHERE LOWER(nome_municipio) = LOWER(?)
                  AND id_uf = ?""", (nome_municipio,id_uf))
    municipio_existente = cursor.fetchone()
    if municipio_existente is not None:
        conn.close()
        raise HTTPException(status_code=409,detail="Este município já está cadastrado neste estado.")
    
    cursor.execute("""SELECT MAX(id_municipio) FROM municipios;""")
    maior_id = cursor.fetchone()["MAX(id_municipio)"]
    novo_id = maior_id + 1
    cursor.execute("""INSERT INTO municipios (id_municipio,nome_municipio,id_uf)
                      VALUES (?, ?, ?)""", (novo_id,nome_municipio,id_uf))
    cursor.execute("""INSERT INTO populacao_municipal (id_municipio,ano,indicador,valor,unidade,fonte)
                          VALUES (?, ?, ?, ?, ?,?)""", (novo_id,ano,indicador,valor,unidade,fonte))

    conn.commit() #usar qnd INSERT, UPDATE, DELETE. nao precisa com SELECT. É confirmar a alteração
    conn.close()
    return {"mensagem": "Cadastro criado com sucesso"}


@router.delete("/municipios/{id_municipio}/ibge")
def deletar_registro_IBGE(id_municipio:int):
    conn = get_connection()
    cursor = conn.cursor()
    verificar_municipio(cursor, id_municipio)

    cursor.execute("""DELETE FROM populacao_municipal WHERE id_municipio = ?""", (id_municipio,))
    cursor.execute("""DELETE FROM municipios WHERE id_municipio = ?""", (id_municipio,))

    conn.commit()
    conn.close()
    return {"mensagem": "Cadastro deletado com sucesso"}


@router.patch("/municipios/{id_municipio}/ibge")
def atualizar_registro_IBGE(id_municipio:int,nome_municipio:str|None=None,id_uf:int|None=None,ano:int|None=None,indicador:str|None=None,valor:int|None=None,unidade:str|None=None,fonte:str|None=None):
    conn = get_connection()
    cursor = conn.cursor()
    verificar_municipio(cursor, id_municipio)

    campos_para_atualizar = []
    campos_para_atualizar_popu = []
    valores = []
    valores_popu = []

    if nome_municipio is not None:
        campos_para_atualizar.append("nome_municipio = ?")
        valores.append(nome_municipio)
    if id_uf is not None:
        campos_para_atualizar.append("id_uf = ?")
        valores.append(id_uf)
    if ano is not None:
        campos_para_atualizar_popu.append("ano = ?")
        valores_popu.append(ano)
    if indicador is not None:
        campos_para_atualizar_popu.append("indicador = ?")
        valores_popu.append(indicador)
    if valor is not None:
        campos_para_atualizar_popu.append("valor = ?")
        valores_popu.append(valor)
    if unidade is not None:
        campos_para_atualizar_popu.append("unidade = ?")
        valores_popu.append(unidade)
    if fonte is not None:
        campos_para_atualizar_popu.append("fonte = ?")
        valores_popu.append(fonte)
    
    if len(campos_para_atualizar) == 0 and len(campos_para_atualizar_popu) == 0:
        raise HTTPException(status_code=400,detail="Nenhum campo enviado.")

    if len(campos_para_atualizar) > 0:
        valores.append(id_municipio)
        campos_para_atualizar = ", ".join(campos_para_atualizar)
        cursor.execute(f"""UPDATE municipios
                        SET {campos_para_atualizar}
                        WHERE id_municipio = ?""", valores)

    if len(campos_para_atualizar_popu) > 0:
        valores_popu.append(id_municipio)
        campos_para_atualizar_popu = ", ".join(campos_para_atualizar_popu)
        cursor.execute(f"""UPDATE populacao_municipal
                        SET {campos_para_atualizar_popu}
                        WHERE id_municipio = ?""", valores_popu)

    conn.commit()
    conn.close()

    return {"mensagem": "Cadastro atualizado com sucesso"}

@router.get("/municipios/{id_municipio}/ibge")
def ler_registro_IBGE(id_municipio:int|None=None):
    conn = get_connection()
    cursor = conn.cursor()
    if id_municipio is not None:
        cursor.execute("""SELECT * FROM municipios WHERE id_municipio = ?""", (id_municipio,))
        municipio = cursor.fetchone()

        cursor.execute("""SELECT * FROM populacao_municipal WHERE id_municipio = ?""", (id_municipio,))
        populacao = cursor.fetchall()

    else: 
        cursor.execute("""SELECT * FROM municipios""")
        municipio = cursor.fetchone()

        cursor.execute("""SELECT * FROM populacao_municipal""")
        populacao = cursor.fetchall()

    conn.close()
    return {"municipio": municipio, "populacao": populacao}


# Etapa 3 de cadastrar novas infos na tabela q criei cadastro_municipio
def criar_tabela_cadastro():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS cadastro_municipios 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,id_municipio INTEGER,
                                prioridade TEXT, obs TEXT, status TEXT,responsavel TEXT,
                                FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio))""")
    conn.commit()
    conn.close()


criar_tabela_cadastro() 

@router.post("/municipios/{id_municipio}/registros")
def criar_registro_gestor(id_municipio:int,prioridade:str,status:str,obs:str,responsavel:str):

    conn = get_connection()
    cursor = conn.cursor()
    verificar_municipio(cursor, id_municipio)
    cursor.execute("""INSERT INTO cadastro_municipios (id_municipio, prioridade, status, obs, responsavel)
                      VALUES (?, ?, ?, ?, ?)""", (id_municipio,prioridade,status,obs,responsavel))

    conn.commit() #usar qnd INSERT, UPDATE, DELETE. nao precisa com SELECT. É confirmar a alteração
    conn.close()
    return {"mensagem": "Cadastro criado com sucesso"}


@router.delete("/municipios/{id_municipio}/registros")
def deletar_registro_gestor(id_municipio:int):

    conn = get_connection()
    cursor = conn.cursor()
    verificar_municipio(cursor, id_municipio)

    cursor.execute("""DELETE FROM cadastro_municipios WHERE id_municipio = ?""", (id_municipio,))

    conn.commit()
    conn.close()
    return {"mensagem": "Cadastro deletado com sucesso"}


@router.patch("/municipios/{id_municipio}/registros")
def atualizar_registro_gestor(id_municipio:int,prioridade:str|None=None,status:str|None=None,obs:str|None=None,responsavel:str|None=None):
    conn = get_connection()
    cursor = conn.cursor()
    verificar_municipio(cursor, id_municipio)

    campos_para_atualizar = []
    valores = []
    if prioridade is not None:
        campos_para_atualizar.append("prioridade = ?")
        valores.append(prioridade)
    if status is not None:
            campos_para_atualizar.append("status = ?")
            valores.append(status)
    if obs is not None:
            campos_para_atualizar.append("obs = ?")
            valores.append(obs)
    if responsavel is not None:
            campos_para_atualizar.append("responsavel = ?")
            valores.append(responsavel)

    valores.append(id_municipio)
    campos_para_atualizar = ", ".join(campos_para_atualizar)
    cursor.execute(f"""UPDATE cadastro_municipios SET {campos_para_atualizar} WHERE id_municipio = ?""", valores)

    conn.commit()
    conn.close()

    return {"mensagem": "Cadastro atualizado com sucesso"}

@router.get("/municipios/{id_municipio}/registros")
def ler_registro_gestor(id_municipio:int|None=None):
    conn = get_connection()
    cursor = conn.cursor()
    if id_municipio is not None:
        cursor.execute("""SELECT * FROM cadastro_municipios WHERE id_municipio = ?""", (id_municipio,))
    else: 
        cursor.execute("""SELECT * FROM cadastro_municipios""")

    resultado = cursor.fetchall()
    conn.close()
    return resultado
