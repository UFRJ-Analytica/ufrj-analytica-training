import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

URL = 'http://127.0.0.1:8000/joao-rodrigo'

st.title("Entrega WebDev")
st.divider()

# kpis
st.header("KPIs")
kpis = requests.get(f'{URL}/estatisticas/resumo')
kpis = kpis.json()

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)
col1.metric("Total de municípios", kpis[0]["total_municipios"])
col2.metric("Total de estados", kpis[0]["total_estados"])
col3.metric("Ano de referência", kpis[0]["ano"])
col4.metric("População total", kpis[0]["populacao_total_br"])
col5.metric("Municipio mais populoso", kpis[0]["municipio_mais_populoso"])

# municipios mais populosos
st.header("Municípios mais populosos")

limite = st.number_input("Quantidade de municípios", 5, 100)

mun = requests.get(f'{URL}/populacao/top-municipios?limit={limite}')
mun = mun.json()

mun_df = pd.DataFrame(mun)

st.table(mun_df)
st.space()
st.bar_chart(mun_df, x="nome_municipio", y="valor", sort=False)

# populacao total por regiao
st.header("População total por região")

pop_regiao = requests.get(f'{URL}/populacao/por-regiao')
pop_regiao = pop_regiao.json()

pop_regiao_df = pd.DataFrame(pop_regiao)

fig1, ax1 = plt.subplots()
ax1.pie(pop_regiao_df["populacao"], labels=pop_regiao_df["nome_regiao"])
ax1.axis('equal')

st.pyplot(fig1)

# populacao total por estado
st.header("População total por estado")

regioes_req = requests.get(f"{URL}/regioes").json()
regioes = [{"id_regiao": None, "nome_regiao": "Todas"}] + regioes_req

regiao = st.selectbox(
    "Regiao",
    options=regioes,
    format_func=lambda r: r["nome_regiao"]
)

params = {}
if regiao["id_regiao"] is not None:
    params["id_regiao"] = regiao["id_regiao"]

pop_estado = requests.get(f'{URL}/populacao/por-uf', params=params)

pop_estado = pop_estado.json()

pop_estado_df = pd.DataFrame(pop_estado)

st.bar_chart(pop_estado_df, x="nome_uf", y="populacao", sort=False)

# distribuicao da populacao
st.header("Distribuição da população")

distribuicao_pop = requests.get(f'{URL}/populacao/distribuicao').json()


distribuicao_pop_df = pd.DataFrame(distribuicao_pop)

st.bar_chart(distribuicao_pop_df, x="inicio", y="quant_municipios", sort=False)

fig = px.scatter(
    distribuicao_pop_df,
    x="inicio", 
    y="quant_municipios",
    log_y=True,
    labels={
        "inicio_intervalo": "Início do intervalo", 
        "quant_municipios": "Quantidade de municípios"
    }
)
# quantidade de municipios x populacao media por estado
st.header("Gráfico de dispersão")

dispersao = requests.get(f'{URL}/populacao/dispersao-uf').json()

dispersao_df = pd.DataFrame(dispersao)

st.scatter_chart(
    dispersao_df,
    x="quant_municipios", 
    y="populacao",
    x_label="Quantidade de municípios",
    y_label="População média",
    color="nome_regiao"
)

# mapa de calor (regiao x porte) 
st.header("Mapa de calor")

mapa_de_calor = requests.get(f'{URL}/populacao/heatmap-regiao-porte').json()

mapa_de_calor_df = pd.DataFrame(mapa_de_calor)

df_pivotado = mapa_de_calor_df.pivot(
    index="nome_regiao",
    columns="categoria",
    values="quant_municipios"
)
fig = px.imshow(df_pivotado, text_auto=True)

st.plotly_chart(fig)

# atualizar, remover e criar um município
st.header("Manipulando municípios")

modos = ("Criar", "Atualizar", "Remover")
modo = st.pills(
        "Ação",
        options=modos,
        selection_mode="single",
)

if modo == "Criar":
    with st.form("criar_municipio"):
        st.subheader("Novo município")
        nome = st.text_input("Nome")
        id_uf = st.number_input("Identificador da unidade federativa", min_value=0)
        populacao = st.number_input("População inicial", min_value=0)
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            data = {
                "nome_municipio": nome,
                "id_uf": id_uf,
                "populacao": populacao
            }
            res = requests.post(f'{URL}/municipios', json=data)
            res.raise_for_status()
            st.success(f"Município {nome} criado")

if modo == "Atualizar":
    with st.form("atualizar_form"):
        st.subheader("Atualizar município")
        id_municipio = st.number_input("Identificador do município", min_value=0)
        nome = st.text_input("Nome")
        id_uf = st.number_input("Identificador da unidade federativa", value=None, min_value=0)
        populacao = st.number_input("População", value=None, min_value=0)
        
        submitted = st.form_submit_button("Atualizar")
        if submitted:
            data = {
                "nome_municipio": nome.strip() if nome and nome.strip() != "" else None,
                "id_uf": int(id_uf) if id_uf is not None else None,
                "populacao": int(populacao) if populacao is not None else None
            }
            res = requests.put(f'{URL}/municipios/{id_municipio}', json=data)
            res.raise_for_status()
            st.success(f"Município de número {id_municipio} alterado")        
        
if modo == "Remover":
    with st.form("remover_municipio"):
        st.subheader("Remover município")
        id_municipio = st.number_input("Identificador do município", min_value=0)
        
        submitted = st.form_submit_button("Remover")
        if submitted:
            res = requests.delete(f'{URL}/municipios/{id_municipio}')
            res.raise_for_status()
            st.success(f"Município de identificador {id_municipio} removido")

# REGISTROS 

st.header("Manipulando registros")

modos = ("Visualizar", "Criar", "Atualizar", "Remover")
modo = st.pills(
        "Ação",
        options=modos,
        selection_mode="single",
)

if modo == "Visualizar":
    with st.form("ver_registro"):
        st.subheader("Visualizar anotações")
        id_municipio = st.number_input("Identificador do município", min_value=0)

        submitted = st.form_submit_button("Pesquisar")
        if submitted:
            try:
                res = requests.get(f"{URL}/municipios/{id_municipio}/registros")
                res.raise_for_status()
                
                anotacoes = res.json()

                if not anotacoes:
                    st.info(f"Nenhuma anotação encontrada para o município {id_municipio}.")
                else:
                    st.markdown(f"### Anotações do município {id_municipio}")
                    
                    for idx, item in enumerate(anotacoes, start=1):
                        st.markdown(f"""
                        #### **Registro #{idx}**  
                        * **ID Anotação:** {item.get('id_anotacao', 'N/A')}  
                        * **Prioridade:** {item.get('prioridade', 'N/A')}  
                        * **Observação:** {item.get('observacao', '')}  
                        * **Responsável:** {item.get('responsavel', '')}
                        """)
                        st.divider()

            except requests.exceptions.HTTPError:
                if res.status_code == 404:
                    st.error(f"Município {id_municipio} não encontrado.")
                else:
                    st.error(f"Erro na API ({res.status_code}): {res.json().get('detail')}")

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao servidor FastAPI.")

if modo == "Criar":
    with st.form("criar_anotacao"):
        st.subheader("Nova anotação")
        id_municipio = st.number_input("Identificador do município", min_value=0)
        observacao = st.text_input("Observação")
        responsavel = st.text_input("Responsável")
        prioridade = st.number_input("Prioridade", value=None, min_value=0, max_value=10)
        
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            data = {
                "prioridade": prioridade,
                "observacao": observacao,
                "responsavel": responsavel
            }
            try:
                res = requests.post(f'{URL}/municipios/{id_municipio}/registros', json=data)
                res.raise_for_status()
                st.success(f"Anotação sobre o município número {id_municipio} registrada")
            
            except requests.exceptions.HTTPError:
                if res.status_code == 404:
                    st.error(f"Município com ID {id_municipio} não existe.")
                elif res.status_code == 422:
                    st.error(f"Dados inválidos: {res.json().get('detail')}")
                else:
                    st.error(f"Erro na API ({res.status_code}): {res.json().get('detail')}")

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao servidor FastAPI.")

if modo == "Atualizar":
    with st.form("atualizar_anotacao"):
        st.subheader("Atualizar anotação")
        id_registro = st.number_input("Identificador do registro", min_value=0)
        observacao = st.text_input("Observação")
        responsavel = st.text_input("Responsável")
        prioridade = st.number_input("Prioridade", value=None, min_value=0, max_value=10)
        
        submitted = st.form_submit_button("Atualizar")
        if submitted:
            data = {}

            if observacao:
                data["observacao"] = observacao
            if responsavel:
                data["responsavel"] = responsavel
            if prioridade is not None:
                data["prioridade"] = prioridade

            try:
                res = requests.put(f'{URL}/registros/{id_registro}', json=data)
                res.raise_for_status()
                st.success(f"Registro número {id_registro} atualizado")
            
            except requests.exceptions.HTTPError:
                if res.status_code == 404:
                    st.error(f"Registro {id_registro} não encontrado")
                else:
                    st.error(f"Erro na API ({res.status_code}): {res.json().get('detail')}")
            except requests.exceptions.ConnectionError:
                st.error("Servidor backend offline.")

if modo == "Remover":
    with st.form("remover_anotacao"):
        st.subheader("Remover anotação")
        id_registro = st.number_input("Identificador da anotação", min_value=1)
        
        submitted = st.form_submit_button("Remover", type="primary")
        if submitted:
            try:
                res = requests.delete(f'{URL}/registros/{id_registro}')
                res.raise_for_status()
                st.success(f"Anotação de identificador {id_registro}")
            
            except requests.exceptions.HTTPError:
                if res.status_code == 404:
                    st.error(f"Anotação {id_registro} não encontrada")
                else:
                    st.error(f"Erro ao remover: {res.json().get('detail')}")

            except requests.exceptions.ConnectionError:
                st.error("Servidor backend offline.")
