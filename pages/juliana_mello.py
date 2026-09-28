import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão Populacional - UFRJ", layout="wide")

st.title("Painel de Acompanhamento Populacional - Gestão")
st.markdown("Bem-vindo ao painel de apoio à decisão para gestores públicos ;)")

API_URL = "http://127.0.0.1:8000/juliana-mello"

# 1. KPIs (Resumo)
st.subheader("Indicadores Gerais (KPIs)")
try:
    response = requests.get(f"{API_URL}/estatisticas/resumo")
    if response.status_code == 200:
        dados = response.json()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Municípios", dados.get("total_municipios", 0))
        col2.metric("Total de Estados", dados.get("total_estados", 0))
        col3.metric("População Total", f"{dados.get('populacao_total', 0):,}")
        col4.metric("Mais Populoso", dados.get("municipio_mais_populoso", "N/A"))
    else:
        st.error("Erro ao carregar o resumo estatístico.")
except Exception:
    st.warning("Não foi possível conectar à API. Verifique se o Uvicorn está rodando.")

# Top Municípios
st.subheader("Top Municípios Mais Populosos")
limit = st.slider("Escolha a quantidade de municípios", min_value=5, max_value=50, value=10)
try:
    response = requests.get(f"{API_URL}/populacao/top-municipios", params={"limit": limit})
    if response.status_code == 200:
        top_dados = response.json()
        df_top = pd.DataFrame(top_dados)
        st.dataframe(df_top, use_container_width=True)
        st.bar_chart(df_top, x="nome_municipio", y="populacao")
    else:
        st.error(f"Erro ao carregar ranking :( (status {response.status_code})")
        st.text(f"Detalhes: {response.text}")
except Exception as e:
    st.error("Erro ao carregar o ranking de municípios.")
    st.text(f"Detalhes do erro: {str(e)}") 

# 3. População por Região
st.subheader("População Total por Região")
try:
    response = requests.get(f"{API_URL}/populacao/por-regiao")
    if response.status_code == 200:
        regiao_dados = response.json()
        df_regiao = pd.DataFrame(regiao_dados)
        st.bar_chart(regiao_dados, x="nome_regiao", y="populacao_total")
        fig = px.pie(df_regiao, names="nome_regiao", values="populacao_total",
                     title= "Pizza da distribuição populacional por região")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Erro ao carregar dados por região :( (status {response.status_code})")
        st.text(f"Detalhes: {response.text}")
except Exception as e:
    st.error("Erro ao carregar os dados por região.")
    st.text(f"Detalhes do erro: {str(e)}")

# 4. População por Estado
st.subheader("População por Estado")
try:
    regioes_resp = requests.get(f"{API_URL}/regioes")
    regioes_dados = regioes_resp.json() if regioes_resp.status_code == 200 else []
    mapa_regioes = {r["nome_regiao"]: r["id_regiao"] for r in regioes_dados}

    regiao_filtro = st.selectbox("Filtrar por região", ["Todas"] + list(mapa_regioes.keys()))

    params = {}
    if regiao_filtro != "Todas":
        params["id_regiao"] = mapa_regioes[regiao_filtro]

    response = requests.get(f"{API_URL}/populacao/por-uf", params=params)
    if response.status_code == 200:
        uf_dados = response.json()
        df_uf = pd.DataFrame(uf_dados)
        st.dataframe(df_uf, use_container_width=True)
        fig = px.bar(df_uf, x="nome_uf", y="populacao_total", title="População por Estado")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Erro ao carregar dados por UF (status {response.status_code})")
except Exception as e:
    st.error("Erro ao carregar dados por UF.")
    st.text(str(e))

# Mapa de calor: região x porte
st.subheader("Mapa de Calor: Região x Porte do Município")
try:
    response = requests.get(f"{API_URL}/populacao/heatmap-porte")
    if response.status_code == 200:
        df_heat = pd.DataFrame(response.json())
        pivot = df_heat.pivot(index="nome_regiao", columns="porte", values="quantidade").fillna(0)
        fig = px.imshow(pivot, text_auto=True, aspect="auto",
                         labels=dict(x="Porte", y="Região", color="Municípios"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Erro ao carregar heatmap (status {response.status_code})")
except Exception as e:
    st.error("Erro ao carregar mapa de calor.")
    st.text(str(e))

# Cadastro de Município (criar / editar / remover)
st.subheader("Cadastro de Município")

with st.form("form_municipio"):
    st.markdown("Criar novo município ou atualizar um existente (informe o ID para atualizar).")
    id_municipio_form = st.number_input("ID do Município (deixe 0 para criar um novo)", min_value=0, step=1, value=0)
    nome_municipio_form = st.text_input("Nome do Município")
    id_uf_form = st.number_input("ID do Estado (id_uf)", min_value=1, step=1)
    populacao_form = st.number_input("População", min_value=0, step=1)

    col_salvar, col_remover = st.columns(2)
    salvar = col_salvar.form_submit_button("Salvar (criar ou atualizar)")
    remover = col_remover.form_submit_button("Remover município")

    if salvar:
        payload = {
            "id_municipio": int(id_municipio_form) if id_municipio_form else 0,
            "nome_municipio": nome_municipio_form,
            "id_uf": int(id_uf_form),
            "populacao": int(populacao_form)
        }
        if id_municipio_form == 0:
            res = requests.post(f"{API_URL}/municipios", json=payload)
        else:
            res = requests.put(f"{API_URL}/municipios/{int(id_municipio_form)}", json=payload)

        if res.status_code == 200:
            resposta = res.json()
            if "id_municipio" in resposta:
                st.success(f"{resposta.get('mensagem', 'Salvo com sucesso!')} ID: {resposta['id_municipio']}")
            else:
                st.success(resposta.get("mensagem", "Salvo com sucesso!"))
        else:
            st.error(f"Erro ao salvar município (status {res.status_code})")
            st.text(res.text)

    if remover:
        if id_municipio_form == 0:
            st.warning("Informe o ID do município que deseja remover.")
        else:
            res = requests.delete(f"{API_URL}/municipios/{int(id_municipio_form)}")
            if res.status_code == 200:
                st.success(res.json().get("mensagem", "Removido com sucesso!"))
            else:
                st.error(f"Erro ao remover município (status {res.status_code})")
                st.text(res.text)

# 5. Gestão / Anotações do Gestor
st.subheader("Registrar Anotação para o Município")

with st.form("form_gestor"):
    id_mun = st.number_input("ID do Município", min_value=1, step=1, value=3304557)
    status_gestor = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído"])
    prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
    observacao = st.text_area("Observações da Gestão")
    responsavel = st.text_input("Responsável")
    
    submitted = st.form_submit_button("Salvar Registro")
    if submitted:
        payload = {
            "status": status_gestor,
            "prioridade": prioridade,
            "observacao": observacao,
            "responsavel": responsavel
        }
        res = requests.post(f"{API_URL}/municipios/{id_mun}/registros", json=payload)
        if res.status_code == 200:
            st.success("Registro salvo com sucesso!")
        else:
            st.error("Erro ao salvar o registro.")

# Distribuição da população
st.subheader("Distribuição da População dos Municípios")
try:
    response = requests.get(f"{API_URL}/populacao/distribuicao")
    if response.status_code == 200:
        df_dist = pd.DataFrame(response.json())
        fig = px.histogram(df_dist, x="valor", nbins=50,
                            title="Distribuição da População Municipal")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Erro ao carregar distribuição (status {response.status_code})")
except Exception as e:
    st.error("Erro ao carregar distribuição populacional.")
    st.text(str(e))

# 6. Consultar / editar / remover registros do gestor
st.subheader("Consultar Registros do Município")
consulta_id = st.number_input("Informe o ID do Município para busca", min_value=1, step=1, value=3304557, key="busca_mun")

if st.button("Buscar Anotações"):
    res = requests.get(f"{API_URL}/municipios/{consulta_id}/registros")
    if res.status_code == 200:
        registros = res.json()
        st.session_state["registros_encontrados"] = registros
    else:
        st.error("Erro ao buscar os registros.")

registros = st.session_state.get("registros_encontrados", [])

if registros:
    st.dataframe(pd.DataFrame(registros), use_container_width=True)

    st.markdown("### Editar ou remover um registro")
    ids_disponiveis = [r["id_registro"] for r in registros]
    id_selecionado = st.selectbox("Escolha o ID do registro", ids_disponiveis)
    registro_atual = next(r for r in registros if r["id_registro"] == id_selecionado)

    with st.form("form_editar_registro"):
        status_edit = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído"],
                                    index=["Pendente", "Em Andamento", "Concluído"].index(registro_atual["status"]) if registro_atual["status"] in ["Pendente", "Em Andamento", "Concluído"] else 0)
        prioridade_edit = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"],
                                        index=["Baixa", "Média", "Alta"].index(registro_atual["prioridade"]) if registro_atual["prioridade"] in ["Baixa", "Média", "Alta"] else 0)
        observacao_edit = st.text_area("Observações", value=registro_atual["observacao"])
        responsavel_edit = st.text_input("Responsável", value=registro_atual["responsavel"])

        col_edit, col_del = st.columns(2)
        salvar_edicao = col_edit.form_submit_button("Salvar edição")
        remover_registro_btn = col_del.form_submit_button("Remover registro")

        if salvar_edicao:
            payload = {
                "status": status_edit,
                "prioridade": prioridade_edit,
                "observacao": observacao_edit,
                "responsavel": responsavel_edit
            }
            res = requests.put(f"{API_URL}/registros/{id_selecionado}", json=payload)
            if res.status_code == 200:
                st.success("Registro atualizado com sucesso!")
            else:
                st.error(f"Erro ao editar registro (status {res.status_code})")

        if remover_registro_btn:
            res = requests.delete(f"{API_URL}/registros/{id_selecionado}")
            if res.status_code == 200:
                st.success("Registro removido com sucesso!")
                st.session_state["registros_encontrados"] = [r for r in registros if r["id_registro"] != id_selecionado]
            else:
                st.error(f"Erro ao remover registro (status {res.status_code})")
elif "registros_encontrados" in st.session_state:
    st.info("Nenhum registro encontrado para este município.")

    
# Dispersão: municípios x população média por estado
st.subheader("Dispersão: Municípios x População Média por Estado")
try:
    response = requests.get(f"{API_URL}/populacao/dispersao-uf")
    if response.status_code == 200:
        df_disp = pd.DataFrame(response.json())
        fig = px.scatter(df_disp, x="qtd_municipios", y="populacao_media",
                          color="nome_regiao", hover_name="nome_uf",
                          title="Municípios x População Média (por região)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Erro ao carregar dispersão (status {response.status_code})")
except Exception as e:
    st.error("Erro ao carregar dispersão.")
    st.text(str(e))



