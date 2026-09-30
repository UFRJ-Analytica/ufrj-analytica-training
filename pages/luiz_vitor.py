import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000/luiz-vitor"

st.set_page_config(page_title="Acompanhamento Populacional - Luiz Vitor", layout="wide")

st.title("Painel de Acompanhamento Populacional do Brasil")
st.markdown("Ferramenta de apoio à decisão para gestores públicos (Dados IBGE 2025 + Anotações de Gestão).")

def testar_api():
    try:
        response = requests.get(f"{API_URL}/status")
        return response.status_code == 200
    except:
        return False

if not testar_api():
    st.error("A API em FastAPI está offline ou inacessível! Suba o servidor com o Uvicorn antes de usar a tela.")
    st.stop()

aba_analise, aba_municipios, aba_gestao = st.tabs(["Análise e Visualizações", "Gestão de Municípios", "Anotações do Gestor"])

with aba_analise:
    st.subheader("Indicadores Resumo (KPIs)")
    try:
        kpis = requests.get(f"{API_URL}/kpis").json()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Municípios", f"{kpis['total_municipios']:,}".replace(",", "."))
        col2.metric("Total de Estados", kpis['total_estados'])
        col3.metric("População Total", f"{kpis['populacao_total_brasil']:,}".replace(",", "."))
        mais_populoso = kpis['municipio_mais_populoso']
        col4.metric("Mais Populoso", f"{mais_populoso['nome']}", f"{mais_populoso['populacao']:,} hab".replace(",", "."))
    except Exception as e:
        st.warning(f"Erro ao carregar KPIs: {e}")

    st.markdown("---")
    
    st.subheader("Top Municípios Mais Populosos")
    limit = st.slider("Selecione a quantidade (Top N):", 5, 30, 10)
    top_data = requests.get(f"{API_URL}/top-municipios?limit={limit}").json()
    if top_data:
        df_top = pd.DataFrame(top_data)
        col_tabela, col_grafico = st.columns(2)
        with col_tabela:
            st.dataframe(df_top, use_container_width=True)
        with col_grafico:
            fig_top = px.bar(df_top, x="nome_municipio", y="populacao", color="sigla_uf", title=f"Top {limit} Municípios")
            st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")
    
    col_reg, col_est = st.columns(2)
    with col_reg:
        st.subheader("População por Região")
        reg_data = requests.get(f"{API_URL}/populacao-regiao").json()
        if reg_data:
            df_reg = pd.DataFrame(reg_data)
            fig_pie = px.pie(df_reg, names="nome_regiao", values="populacao_total", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_est:
        st.subheader("População por Estado")
        regioes_disp = [r["nome_regiao"] for r in reg_data] if reg_data else []
        filtro_regiao = st.selectbox("Filtrar por Região (Opcional):", ["Todas"] + regioes_disp)
        
        url_est = f"{API_URL}/populacao-estado"
        if filtro_regiao != "Todas":
            url_est += f"?regiao={filtro_regiao}"
            
        est_data = requests.get(url_est).json()
        if est_data:
            df_est = pd.DataFrame(est_data)
            fig_est = px.bar(df_est, x="sigla_uf", y="populacao_total", color="nome_regiao")
            st.plotly_chart(fig_est, use_container_width=True)

    st.markdown("---")
    
    col_hist, col_disc = st.columns(2)
    with col_hist:
        st.subheader("Distribuição Populacional (Histograma)")
        pop_vals = requests.get(f"{API_URL}/distribuicao-populacao").json()
        if pop_vals:
            df_pop = pd.DataFrame({"populacao": pop_vals})
            fig_hist = px.histogram(df_pop, x="populacao", nbins=50, log_y=True, title="Escala Logarítmica de População")
            st.plotly_chart(fig_hist, use_container_width=True)

    with col_disc:
        st.subheader("Municípios x População Média por UF")
        disc_data = requests.get(f"{API_URL}/dispersao-estado").json()
        if disc_data:
            df_disc = pd.DataFrame(disc_data)
            fig_disc = px.scatter(df_disc, x="qtd_municipios", y="populacao_media", color="nome_regiao", text="sigla_uf")
            st.plotly_chart(fig_disc, use_container_width=True)

    st.subheader("Mapa de Calor: Região x Porte do Município")
    heat_data = requests.get(f"{API_URL}/heatmap-porte").json()
    if heat_data:
        df_heat = pd.DataFrame(heat_data)
        df_pivot = df_heat.pivot(index="nome_regiao", columns="porte", values="quantidade").fillna(0)
        fig_heat = px.imshow(df_pivot, text_auto=True, title="Matriz Região x Porte")
        st.plotly_chart(fig_heat, use_container_width=True)

with aba_municipios:
    st.subheader("Cadastro e Atualização de Municípios")
    
    with st.form("form_novo_municipio"):
        st.markdown("### Adicionar Novo Município")
        nome_mun = st.text_input("Nome do Município")
        id_uf = st.number_input("ID do Estado (UF)", min_value=11, max_value=53, value=33)
        pop_mun = st.number_input("População Estimada", min_value=1, value=50000)
        submit_mun = st.form_submit_button("Cadastrar Município")
        
        if submit_mun:
            payload = {"nome_municipio": nome_mun, "id_uf": int(id_uf), "populacao": int(pop_mun)}
            res = requests.post(f"{API_URL}/municipios", json=payload)
            if res.status_code == 200:
                st.success("Município cadastrado com sucesso! Atualize a página.")
            else:
                st.error(f"Erro ao cadastrar: {res.text}")

    st.markdown("---")
    st.markdown("### Editar ou Remover Município Existente")
    id_edit = st.number_input("ID do Município para Editar/Remover", min_value=1, value=1)
    novo_nome = st.text_input("Novo Nome (deixe em branco se não quiser mudar)")
    nova_pop = st.number_input("Nova População (0 para ignorar)", min_value=0, value=0)
    
    col_upd, col_del = st.columns(2)
    with col_upd:
        if st.button("Atualizar Município"):
            payload = {}
            if novo_nome: payload["nome_municipio"] = novo_nome
            if nova_pop > 0: payload["populacao"] = int(nova_pop)
            res = requests.put(f"{API_URL}/municipios/{id_edit}", json=payload)
            if res.status_code == 200:
                st.success("Atualizado com sucesso!")
            else:
                st.error(f"Erro: {res.text}")
    with col_del:
        if st.button("Remover Município", type="primary"):
            res = requests.delete(f"{API_URL}/municipios/{id_edit}")
            if res.status_code == 200:
                st.success("Removido com sucesso!")
            else:
                st.error(f"Erro: {res.text}")

with aba_gestao:
    st.subheader("Anotações e Acompanhamento Gerencial")
    
    cadastros = requests.get(f"{API_URL}/cadastro-gestor").json()
    if cadastros:
        st.dataframe(pd.DataFrame(cadastros), use_container_width=True)
    else:
        st.info("Nenhum registro gerencial cadastrado até o momento.")
        
    st.markdown("---")
    
    with st.form("form_gestor"):
        st.markdown("### Registrar Anotação para um Município")
        id_m = st.number_input("ID do Município", min_value=1, value=1)
        status_g = st.selectbox("Status", ["monitorando", "crescimento rápido", "estável", "crítico"])
        prioridade_g = st.selectbox("Prioridade", ["baixa", "media", "alta", "urgente"])
        obs_g = st.text_area("Observação / Motivo")
        resp_g = st.text_input("Responsável pela Anotação")
        
        sub_gestor = st.form_submit_button("Salvar Anotação")
        if sub_gestor:
            payload = {
                "id_municipio": int(id_m),
                "status": status_g,
                "prioridade": prioridade_g,
                "observacao": obs_g,
                "responsavel": resp_g
            }
            res = requests.post(f"{API_URL}/cadastro-gestor", json=payload)
            if res.status_code == 200:
                st.success("Anotação salva com sucesso!")
            else:
                st.error(f"Erro: {res.text}")

    st.markdown("---")
    st.markdown("### Remover Anotação do Gestor")
    id_reg_del = st.number_input("ID do Registro Gerencial (id_cadastro) para Apagar", min_value=1, value=1)
    if st.button("Apagar Registro Gerencial"):
        res = requests.delete(f"{API_URL}/cadastro-gestor/{id_reg_del}")
        if res.status_code == 200:
            st.success("Registro apagado com sucesso!")
        else:
            st.error(f"Erro: {res.text}")