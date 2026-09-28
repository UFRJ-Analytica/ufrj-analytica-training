import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Painel Populacional - Caroline Nomura", layout="wide")
st.title("Dashboard de Acompanhamento Populacional")

API_URL = "http://127.0.0.1:8000/caroline-nomura"

def buscar_kpis():
    try:
        resposta = requests.get(f"{API_URL}/kpis")
        resposta.raise_for_status() 
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_top_municipios(n):
    try:
        resposta = requests.get(f"{API_URL}/municipios/top", params={"n": n})
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_populacao_regiao():
    try:
        resposta = requests.get(f"{API_URL}/regioes/populacao")
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_populacao_estado(regiao=None):
    params = {"regiao": regiao} if regiao and regiao != "Todas" else {}
    try:
        resposta = requests.get(f"{API_URL}/estados/populacao", params=params)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_distribuicao():
    try:
        resposta = requests.get(f"{API_URL}/municipios/distribuicao")
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_dispersao():
    try:
        resposta = requests.get(f"{API_URL}/estados/dispersao")
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

def buscar_heatmap():
    try:
        resposta = requests.get(f"{API_URL}/municipios/heatmap")
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return None

# CRUD DE MUNICIPIOS
def criar_municipio(nome, id_uf, populacao):
    payload = {"nome_municipio": nome, "id_uf": id_uf, "populacao": populacao}
    return requests.post(f"{API_URL}/municipios", json=payload)

def atualizar_municipio(id_mun, nome, id_uf, populacao):
    payload = {"nome_municipio": nome, "id_uf": id_uf, "populacao": populacao}
    return requests.put(f"{API_URL}/municipios/{id_mun}", json=payload)

def deletar_municipio(id_mun):
    return requests.delete(f"{API_URL}/municipios/{id_mun}")

# CRUD DE ACOMPANHAMENTOS/OBSERVAÇÕES DO GESTOR
def listar_acompanhamentos():
    try:
        resposta = requests.get(f"{API_URL}/acompanhamentos")
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException:
        return []

def criar_acompanhamento(id_mun, status, prio, obs, resp):
    payload = {
        "id_municipio": id_mun,
        "status": status,
        "prioridade": prio,
        "observacao": obs,
        "responsavel": resp
    }
    return requests.post(f"{API_URL}/acompanhamentos", json=payload)

def atualizar_acompanhamento(id_acomp, id_mun, status, prio, obs, resp):
    payload = {
        "id_municipio": id_mun,
        "status": status,
        "prioridade": prio,
        "observacao": obs,
        "responsavel": resp
    }
    return requests.put(f"{API_URL}/acompanhamentos/{id_acomp}", json=payload)

def deletar_acompanhamento(id_acomp):
    return requests.delete(f"{API_URL}/acompanhamentos/{id_acomp}")

# SEÇÃO DE ANÁLISE
st.header("Análise geral")

kpis = buscar_kpis()

# Renderiza os KPIs 
if kpis:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total de municípios", kpis["total_municipios"])
    col2.metric("Total de estados", kpis["total_estados"])
    
    pop_formatada = f"{kpis['populacao_total']:,}".replace(",", ".")
    col3.metric("População total", pop_formatada)
    
    col4.metric("Ano referência", kpis["ano_referencia"])
    col5.metric("Mais populoso", kpis["municipio_mais_populoso"])
else:
    st.error("A API está fora do ar. Verifique se o servidor Uvicorn está rodando no terminal.")

st.divider()

# SEÇÃO DE GRÁFICOS
st.subheader("Visualizações")

col_top, col_regiao = st.columns(2)

with col_top:
    st.markdown("### Municípios mais populosos")
    n_selecionado = st.slider("Quantidade de municípios", min_value=5, max_value=50, value=10, step=5)
    
    dados_top = buscar_top_municipios(n_selecionado)
    if dados_top:
        df_top = pd.DataFrame(dados_top)
        
        st.dataframe(df_top, use_container_width=True, hide_index=True)
        st.bar_chart(df_top, x="nome_municipio", y="populacao")

with col_regiao:
    st.markdown("### População por região")
    dados_regiao = buscar_populacao_regiao()
    if dados_regiao:
        df_regiao = pd.DataFrame(dados_regiao)
        
        fig_donut = px.pie(
            df_regiao, 
            values='populacao_total', 
            names='nome_regiao', 
            hole=0.4, 
        )
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0)) 
        st.plotly_chart(fig_donut, use_container_width=True)

st.divider()

col_estado, col_hist = st.columns(2)

with col_estado:
    st.markdown("### População por estado")
    
    regioes_opcoes = ["Todas", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
    regiao_selecionada = st.selectbox("Filtrar por região", regioes_opcoes)
    
    dados_estado = buscar_populacao_estado(regiao_selecionada)
    if dados_estado:
        df_estado = pd.DataFrame(dados_estado)
        fig_barras = px.bar(
            df_estado, x='sigla_uf', y='populacao_total', 
            labels={'sigla_uf': 'Estado', 'populacao_total': 'População'}
        )
        st.plotly_chart(fig_barras, use_container_width=True)

with col_hist:
    st.markdown("### Distribuição da população")
    dados_dist = buscar_distribuicao()
    if dados_dist:
        df_dist = pd.DataFrame(dados_dist)
        # Histograma
        fig_hist = px.histogram(
            df_dist, x="populacao", nbins=50,
            labels={'populacao': 'População do município'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

col_scatter, col_heat = st.columns(2)

with col_scatter:
    st.markdown("### Dispersão: Municípios x População média")
    dados_disp = buscar_dispersao()
    if dados_disp:
        df_disp = pd.DataFrame(dados_disp)
        # Scatter plot colorido pela região
        fig_scatter = px.scatter(
            df_disp, x="quantidade_municipios", y="populacao_media", 
            color="nome_regiao", hover_name="sigla_uf", size_max=60,
            labels={'quantidade_municipios': 'Qtd de Municípios', 'populacao_media': 'População Média', 'nome_regiao': 'Região'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with col_heat:
    st.markdown("### Mapa de calor: Região x Porte")
    dados_heat = buscar_heatmap()
    if dados_heat:
        df_heat = pd.DataFrame(dados_heat)
        # Plotly agrupa e pinta o heatmap com base na quantidade 'z'
        fig_heat = px.density_heatmap(
            df_heat, x="porte", y="nome_regiao", z="quantidade_municipios", 
            histfunc="sum", color_continuous_scale="Viridis", text_auto=True,
            labels={'porte': 'Porte', 'nome_regiao': 'Região', 'quantidade_municipios': 'Quantidade'}
        )
        fig_heat.update_xaxes(categoryorder='array', categoryarray=['Pequeno', 'Médio', 'Grande'])
        st.plotly_chart(fig_heat, use_container_width=True)

# SEÇÃO DE CADASTRO
st.divider()
st.header("Gestão e cadastro")

tab_mun, tab_gestor = st.tabs(["Municípios", "Anotações do gestor"])

with tab_mun:
    col_criar, col_editar = st.columns(2)
    
    # Formulário para criar município
    with col_criar:
        st.subheader("Cadastrar município")
        with st.form("form_criar_mun"):
            nome_novo = st.text_input("Nome do município")
            uf_novo = st.number_input("ID do estado (UF)", min_value=11, max_value=53, step=1)
            pop_nova = st.number_input("População estimada", min_value=0, step=1)
            
            submit_criar = st.form_submit_button("Cadastrar")
            if submit_criar:
                res = criar_municipio(nome_novo, uf_novo, pop_nova)
                if res.status_code == 201:
                    st.success(f"Município criado com sucesso! ID gerado: {res.json()['id_municipio']}")
                else:
                    st.error("Erro ao criar município.")

    # Formulários para atualizar e remover município
    with col_editar:
        st.subheader("Atualizar ou remover município")
        id_alvo = st.number_input("ID do Município alvo", min_value=1, step=1)
        
        with st.form("form_atualizar_mun"):
            st.markdown("**Novos dados (para atualização):**")
            nome_edit = st.text_input("Novo nome")
            uf_edit = st.number_input("Novo ID do estado", min_value=11, max_value=53, step=1)
            pop_edit = st.number_input("Nova população", min_value=0, step=1)
            
            submit_atualizar = st.form_submit_button("Atualizar município")
            if submit_atualizar:
                res = atualizar_municipio(id_alvo, nome_edit, uf_edit, pop_edit)
                if res.status_code == 200:
                    st.success("Município atualizado com sucesso!")
                else:
                    st.error("Erro ao atualizar ou município não encontrado.")
        
        if st.button("Remover município", type="primary"):
            res = deletar_municipio(id_alvo)
            if res.status_code == 200:
                st.success("Município e dados dependentes removidos!")
            else:
                st.error("Erro ao remover ou município não encontrado.")

with tab_gestor:
    st.markdown("### Visualizar anotações")
    lista_acomp = listar_acompanhamentos()
    
    if lista_acomp:
        df_acomp = pd.DataFrame(lista_acomp)
        st.dataframe(df_acomp, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhuma anotação de gestor encontrada no banco de dados.")
        
    st.divider()
    
    col_criar_acomp, col_editar_acomp = st.columns(2)
    
    # Formulário para criar anotação
    with col_criar_acomp:
        st.subheader("Cadastrar anotação")
        with st.form("form_criar_acomp"):
            id_mun_acomp = st.number_input("ID do município (existente)", min_value=1, step=1, key="add_mun")
            status_acomp = st.selectbox("Status", ["Em observação", "Alerta", "Resolvido"], key="add_status")
            prioridade_acomp = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"], key="add_prio")
            responsavel_acomp = st.text_input("Nome do responsável", key="add_resp")
            obs_acomp = st.text_area("Observação detalhada", key="add_obs")
            
            submit_acomp = st.form_submit_button("Salvar anotação")
            if submit_acomp:
                res = criar_acompanhamento(id_mun_acomp, status_acomp, prioridade_acomp, obs_acomp, responsavel_acomp)
                if res.status_code == 201:
                    st.success("Anotação salva com sucesso! Atualize a página para ver na tabela.")
                else:
                    st.error("Erro ao salvar. Verifique se o ID do Município existe.")

    # Formulários para atualizar e remover anotação
    with col_editar_acomp:
        st.subheader("Atualizar ou remover anotação")
        id_alvo_acomp = st.number_input("ID da anotação (veja na tabela)", min_value=1, step=1, key="edit_id")
        
        with st.form("form_atualizar_acomp"):
            st.markdown("**Novos dados (para atualização):**")
            id_mun_edit = st.number_input("ID do município", min_value=1, step=1, key="edit_mun")
            status_edit = st.selectbox("Status", ["Em observação", "Alerta", "Resolvido"], key="edit_status")
            prioridade_edit = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"], key="edit_prio")
            responsavel_edit = st.text_input("Responsável", key="edit_resp")
            obs_edit = st.text_area("Observação", key="edit_obs")
            
            submit_edit_acomp = st.form_submit_button("Atualizar anotação")
            if submit_edit_acomp:
                res = atualizar_acompanhamento(id_alvo_acomp, id_mun_edit, status_edit, prioridade_edit, obs_edit, responsavel_edit)
                if res.status_code == 200:
                    st.success("Anotação atualizada com sucesso! Atualize a página.")
                else:
                    st.error("Erro ao atualizar anotação. Verifique os IDs.")
                    
        if st.button("Remover anotação", type="primary", key="del_acomp"):
            res = deletar_acompanhamento(id_alvo_acomp)
            if res.status_code == 200:
                st.success("Anotação removida com sucesso! Atualize a página.")
            else:
                st.error("Erro ao remover anotação.")
