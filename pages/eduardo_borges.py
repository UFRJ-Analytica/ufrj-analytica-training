import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# URL Base da sua API FastAPI
API_URL = "http://127.0.0.1:8000/eduardo-borges"

st.set_page_config(page_title="Painel Eduardo Borges", layout="wide")
st.title("📊 Sistema de Acompanhamento Populacional - Eduardo Borges")

# Função auxiliar para testar a conexão com a API
def fetch_data(endpoint: str, params: dict = None):
    try:
        res = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Erro na requisição: {res.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Não foi possível conectar à API. Verifique se o servidor FastAPI (Uvicorn) está rodando!")
        return None

# ==========================================================
# TESTE DE CONEXÃO E CRIAÇÃO DAS ABAS
# ==========================================================
kpis = fetch_data("/kpis")

if kpis:
    # Criação das Abas Principais
    aba_analise, aba_municipios, aba_gestor = st.tabs([
        "📈 Análise & Gráficos", 
        "🏛️ Gestão de Municípios", 
        "📝 Anotações do Gestor"
    ])

    # ------------------------------------------------------
    # ABA 1: ANÁLISE & GRÁFICOS
    # ------------------------------------------------------
    with aba_analise:
        # 1. KPIs no topo
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Municípios", f"{kpis['total_municipios']:,}".replace(",", "."))
        col2.metric("Total de Estados", kpis["total_estados"])
        col3.metric("População Brasil", f"{kpis['populacao_total_brasil']:,}".replace(",", "."))
        col4.metric(f"Mais Populoso ({kpis['municipio_mais_populoso']})", f"{kpis['populacao_mais_populoso']:,}".replace(",", "."))

        st.markdown("---")

        # 2. Top N Municípios + Filtro
        col_esq, col_dir = st.columns([1, 2])
        with col_esq:
            st.subheader("Top Municípios")
            top_n = st.slider("Selecione a quantidade (Top N):", 5, 20, 10)
            dados_top = fetch_data("/top_municipios", params={"limit": top_n})
            if dados_top:
                df_top = pd.DataFrame(dados_top)
                st.dataframe(df_top, use_container_width=True)
        
        with col_dir:
            if dados_top:
                fig_top = px.bar(
                    df_top, x="nome_municipio", y="populacao", color="uf",
                    title=f"Top {top_n} Municípios Mais Populosos",
                    labels={"nome_municipio": "Município", "populacao": "População"}
                )
                st.plotly_chart(fig_top, use_container_width=True)

        st.markdown("---")

        # 3. Pizza por Região e Barras por Estado
        col_reg, col_est = st.columns(2)
        with col_reg:
            st.subheader("População por Região")
            dados_reg = fetch_data("/populacao_por_regiao")
            if dados_reg:
                df_reg = pd.DataFrame(dados_reg)
                fig_reg = px.pie(df_reg, names="nome_regiao", values="populacao_total", hole=0.4, title="Fatia Populacional por Região")
                st.plotly_chart(fig_reg, use_container_width=True)

        with col_est:
            st.subheader("População por Estado")
            dados_est = fetch_data("/populacao_por_estado")
            if dados_est:
                df_est = pd.DataFrame(dados_est)
                fig_est = px.bar(df_est, x="uf", y="populacao_total", color="nome_regiao", title="População por Estado (UF)")
                st.plotly_chart(fig_est, use_container_width=True)

        st.markdown("---")

        # 4. Histograma + Scatter Plot
        col_hist, col_scat = st.columns(2)
        with col_hist:
            st.subheader("Distribuição da População")
            dados_dist = fetch_data("/distribuicao_populacao")
            if dados_dist:
                fig_hist = px.histogram(dados_dist, nbins=50, title="Histograma do Porte dos Municípios", labels={"value": "População"})
                st.plotly_chart(fig_hist, use_container_width=True)

        with col_scat:
            st.subheader("Dispersão: Qtd Municípios x Pop. Média")
            dados_disp = fetch_data("/dispersao_municipios_estado")
            if dados_disp:
                df_disp = pd.DataFrame(dados_disp)
                fig_disp = px.scatter(
                    df_disp, x="qtd_municipios", y="populacao_media", color="nome_regiao", hover_name="nome_estado",
                    title="Quantidade de Municípios vs População Média por Estado"
                )
                st.plotly_chart(fig_disp, use_container_width=True)

        # 5. Heatmap Porte x Região
        st.markdown("---")
        st.subheader("Mapa de Calor: Região x Porte do Município")
        dados_heat = fetch_data("/heatmap_porte_regiao")
        if dados_heat:
            df_heat = pd.DataFrame(dados_heat).set_index("nome_regiao")
            fig_heat = px.imshow(df_heat, text_auto=True, color_continuous_scale="Blues", title="Contagem de Municípios por Porte e Região")
            st.plotly_chart(fig_heat, use_container_width=True)

    # ------------------------------------------------------
    # ABA 2: GESTÃO DE MUNICÍPIOS (CRUD)
    # ------------------------------------------------------
    with aba_municipios:
        st.header("Cadastrar / Editar Município")
        
        col_cad1, col_cad2 = st.columns(2)
        with col_cad1:
            st.subheader("Novo Município")
            with st.form("form_novo_mun"):
                nome_mun = st.text_input("Nome do Município")
                id_uf_mun = st.number_input("ID do Estado (id_uf)", min_value=1, max_value=27, value=1)
                pop_mun = st.number_input("População Inicial", min_value=1, value=10000)
                submetido = st.form_submit_button("Cadastrar Município")
                
                if submetido:
                    payload = {"nome_municipio": nome_mun, "id_uf": id_uf_mun, "populacao": pop_mun}
                    res = requests.post(f"{API_URL}/municipios", json=payload)
                    if res.status_code == 201:
                        st.success("Município cadastrado com sucesso!")
                    else:
                        st.error(f"Erro ao cadastrar: {res.text}")

        with col_cad2:
            st.subheader("Editar / Excluir Município")
            id_edit = st.number_input("ID do Município para alterar", min_value=1, value=1)
            novo_nome = st.text_input("Novo Nome (opcional)")
            nova_pop = st.number_input("Nova População (0 para manter)", min_value=0, value=0)
            
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("Atualizar Dados"):
                payload = {}
                if novo_nome: payload["nome_municipio"] = novo_nome
                if nova_pop > 0: payload["populacao"] = nova_pop
                res = requests.put(f"{API_URL}/municipios/{id_edit}", json=payload)
                if res.status_code == 200:
                    st.success("Município atualizado!")
                else:
                    st.error("Erro ao atualizar.")

            if col_b2.button("Excluir Município", type="primary"):
                res = requests.delete(f"{API_URL}/municipios/{id_edit}")
                if res.status_code == 200:
                    st.warning("Município removido!")
                else:
                    st.error("Erro ao remover.")

    # ------------------------------------------------------
    # ABA 3: ANOTAÇÕES DO GESTOR
    # ------------------------------------------------------
    with aba_gestor:
        st.header("Anotações e Observações do Gestor")
        
        # Form de Cadastro de Observação
        with st.expander("➕ Nova Anotação"):
            with st.form("form_obs"):
                id_mun_obs = st.number_input("ID do Município Alvo", min_value=1, value=1)
                status_obs = st.selectbox("Status", ["Em Acompanhamento", "Pendente", "Concluído"])
                prioridade_obs = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
                responsavel_obs = st.text_input("Nome do Responsável")
                texto_obs = st.text_area("Observação / Detalhes")
                sub_obs = st.form_submit_button("Salvar Anotação")
                
                if sub_obs:
                    payload_obs = {
                        "id_municipio": id_mun_obs, "status": status_obs,
                        "prioridade": prioridade_obs, "observacao": texto_obs,
                        "responsavel": responsavel_obs
                    }
                    res = requests.post(f"{API_URL}/observacoes", json=payload_obs)
                    if res.status_code == 201:
                        st.success("Anotação registrada com sucesso!")
                    else:
                        st.error("Erro ao salvar anotação.")

        # Tabela de Anotações Cadastradas
        st.subheader("Anotações Registradas")
        obs_dados = fetch_data("/observacoes")
        if obs_dados:
            st.dataframe(pd.DataFrame(obs_dados), use_container_width=True)
        else:
            st.info("Nenhuma anotação cadastrada até o momento.")