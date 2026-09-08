import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE_URL = "http://127.0.0.1:8000/pedro-tonelli"

st.set_page_config(page_title="Painel Populacional - Pedro Tonelli", layout="wide")
st.title("📊 Sistema de Acompanhamento Populacional (IBGE)")

# Função auxiliar para realizar chamadas à API
def fetch_api(endpoint, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API ({endpoint}): {response.status_code}")
            return None
    except Exception as e:
        st.error(f"A API está offline ou inacessível! Erro: {e}")
        return None

# Abas do Sistema
tab_analise, tab_municipios, tab_gestao = st.tabs(["📈 Painel de Análise", "🏙️ Cadastrar/Editar Municípios", "📝 Anotações do Gestor"])

# ==================== ABA 1: PAINEL DE ANÁLISE ====================
with tab_analise:
    kpis = fetch_api("kpis")
    if kpis:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de Municípios", f"{kpis['total_municipios']:,}")
        c2.metric("Total de Estados", kpis['total_estados'])
        c3.metric("População do Brasil", f"{kpis['populacao_total']:,}")
        c4.metric("Mais Populoso", f"{kpis['municipio_mais_populoso']}", f"{kpis['populacao_mais_populoso']:,} hab.")
        st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top N Municípios mais Populosos")
        top_n = st.slider("Escolha a quantidade (N):", 5, 30, 10)
        data_top = fetch_api("top-municipios", params={"n": top_n})
        if data_top:
            df_top = pd.DataFrame(data_top)
            fig_top = px.bar(df_top, x="populacao", y="nome_municipio", color="sigla_uf", orientation='h', 
                             title=f"Top {top_n} Municípios", labels={"populacao": "População", "nome_municipio": "Município"})
            st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        st.subheader("População por Região")
        data_reg = fetch_api("populacao-regiao")
        if data_reg:
            df_reg = pd.DataFrame(data_reg)
            fig_reg = px.pie(df_reg, values="populacao_total", names="nome_regiao", hole=0.4, title="Distribuição por Região")
            st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("---")
    c_est, c_hist = st.columns(2)

    with c_est:
        st.subheader("População por Estado")
        reg_filter = st.selectbox("Filtrar por Região:", ["Todas", "1 - Norte", "2 - Nordeste", "3 - Sudeste", "4 - Sul", "5 - Centro-Oeste"])
        reg_id = int(reg_filter.split(" - ")[0]) if reg_filter != "Todas" else None
        data_est = fetch_api("populacao-estado", params={"regiao_id": reg_id} if reg_id else None)
        if data_est:
            df_est = pd.DataFrame(data_est)
            fig_est = px.bar(df_est, x="sigla_uf", y="populacao_total", color="sigla_uf", title="População Total por Estado")
            st.plotly_chart(fig_est, use_container_width=True)

    with c_hist:
        st.subheader("Distribuição da População dos Municípios")
        data_dist = fetch_api("distribuicao-populacao")
        if data_dist:
            fig_hist = px.histogram(data_dist, nbins=50, title="Histograma de População (Escala Logarítmica)", log_y=True)
            st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")
    c_disp, c_heat = st.columns(2)

    with c_disp:
        st.subheader("Municípios x População Média por Estado")
        data_disp = fetch_api("dispersao-estado")
        if data_disp:
            df_disp = pd.DataFrame(data_disp)
            fig_disp = px.scatter(df_disp, x="qtd_municipios", y="populacao_media", color="nome_regiao", text="sigla_uf",
                                  title="Dispersão: Qtd Municípios vs População Média")
            st.plotly_chart(fig_disp, use_container_width=True)

    with c_heat:
        st.subheader("Mapa de Calor: Região x Porte")
        data_heat = fetch_api("heatmap-porte")
        if data_heat:
            df_heat = pd.DataFrame(data_heat)
            df_pivot = df_heat.pivot(index="nome_regiao", columns="porte", values="quantidade").fillna(0)
            fig_heat = px.imshow(df_pivot, text_auto=True, title="Matriz de Região por Porte")
            st.plotly_chart(fig_heat, use_container_width=True)

# ==================== ABA 2: CRUD DE MUNICÍPIOS ====================
with tab_municipios:
    st.header("Gerenciamento de Municípios")
    action_muni = st.radio("Ação:", ["Novo Município", "Editar Município", "Deletar Município"], horizontal=True)

    if action_muni == "Novo Município":
        with st.form("form_novo_muni"):
            nome = st.text_input("Nome do Município:")
            id_uf = st.number_input("ID do Estado (id_uf, ex: 33 para RJ):", min_value=1, value=33)
            populacao = st.number_input("População:", min_value=0, value=10000)
            submitted = st.form_submit_button("Cadastrar Município")
            if submitted:
                res = requests.post(f"{API_BASE_URL}/municipios", json={"nome_municipio": nome, "id_uf": id_uf, "populacao": populacao})
                if res.status_code == 201:
                    st.success(f"Município criado com sucesso! ID: {res.json()['id_municipio']}")
                else:
                    try:
                        detalhe_erro = res.json().get("detail", res.text)
                    except:
                        detalhe_erro = res.text
                    st.error(f"Erro {res.status_code} ao cadastrar município: {detalhe_erro}")

    elif action_muni == "Editar Município":
        muni_id_edit = st.number_input("ID do Município para Editar:", min_value=1, step=1)
        novo_nome = st.text_input("Novo Nome (opcional):")
        novo_uf = st.number_input("Novo ID UF (opcional, 0 para manter):", min_value=0, value=0)
        nova_pop = st.number_input("Nova População (opcional, -1 para manter):", min_value=-1, value=-1)
        if st.button("Atualizar Município"):
            payload = {}
            if novo_nome: payload["nome_municipio"] = novo_nome
            if novo_uf > 0: payload["id_uf"] = novo_uf
            if nova_pop >= 0: payload["populacao"] = nova_pop
            res = requests.put(f"{API_BASE_URL}/municipios/{muni_id_edit}", json=payload)
            if res.status_code == 200:
                st.success("Município atualizado!")
            else:
                try:
                    detalhe_erro = res.json().get("detail", res.text)
                except:
                    detalhe_erro = res.text
                st.error(f"Erro {res.status_code} ao atualizar município: {detalhe_erro}")

    elif action_muni == "Deletar Município":
        muni_id_del = st.number_input("ID do Município para Deletar:", min_value=1, step=1)
        if st.button("Remover Município", type="primary"):
            res = requests.delete(f"{API_BASE_URL}/municipios/{muni_id_del}")
            if res.status_code == 200:
                st.success("Município deletado!")
            else:
                try:
                    detalhe_erro = res.json().get("detail", res.text)
                except:
                    detalhe_erro = res.text
                st.error(f"Erro {res.status_code} ao remover município: {detalhe_erro}")

# ==================== ABA 3: CRUD DE ANOTAÇÕES ====================
with tab_gestao:
    st.header("Anotações e Acompanhamento do Gestor")
    
    st.subheader("Registrar Nova Anotação")
    with st.form("form_anotacao"):
        id_muni_anot = st.number_input("ID do Município:", min_value=1, step=1)
        status_anot = st.selectbox("Status:", ["Em Monitoramento", "Prioridade Alta", "Resolvido", "Pendente"])
        prioridade_anot = st.selectbox("Prioridade:", ["Baixa", "Média", "Alta", "Urgente"])
        responsavel_anot = st.text_input("Nome do Responsável:")
        obs_anot = st.text_area("Observação do Gestor:")
        
        submit_anot = st.form_submit_button("Salvar Anotação")
        if submit_anot:
            payload = {
                "id_municipio": id_muni_anot,
                "status": status_anot,
                "prioridade": prioridade_anot,
                "responsavel": responsavel_anot,
                "observacao": obs_anot
            }
            res = requests.post(f"{API_BASE_URL}/anotacoes", json=payload)
            if res.status_code == 201:
                st.success("Anotação salva com sucesso!")
            else:
                try:
                    detalhe_erro = res.json().get("detail", res.text)
                except:
                    detalhe_erro = res.text
                st.error(f"Erro {res.status_code} ao salvar anotação: {detalhe_erro}")

    st.markdown("---")
    st.subheader("Anotações Registradas")
    data_anot = fetch_api("anotacoes")
    if data_anot:
        df_anot = pd.DataFrame(data_anot)
        st.dataframe(df_anot, use_container_width=True)
        
        c_del_anot, c_edit_anot = st.columns(2)
        with c_del_anot:
            id_del = st.number_input("ID da Anotação para Deletar:", min_value=1, step=1)
            if st.button("Deletar Anotação"):
                res = requests.delete(f"{API_BASE_URL}/anotacoes/{id_del}")
                if res.status_code == 200:
                    st.success("Anotação removida!")
                else:
                    try:
                        detalhe_erro = res.json().get("detail", res.text)
                    except:
                        detalhe_erro = res.text
                    st.error(f"Erro {res.status_code} ao remover anotação: {detalhe_erro}")