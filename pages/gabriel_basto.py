import streamlit as st
import requests
import pandas as pd
import plotly.express as px


URL_BACKEND = "http://127.0.0.1:8000/gabriel-basto"

st.set_page_config(page_title="Indicadores Demográficos", layout="wide", initial_sidebar_state="expanded")
st.title("🗺️ Painel de Indicadores Demográficos | IBGE 2025")
st.markdown("Plataforma analítica para extração de dados brutos populacionais e gestão de acompanhamento.")

# Função para consumir a API com tratamento de exceções refinado
def get_dados_brutos_api(rota, parametros=None):
    try:
        resposta = requests.get(f"{URL_BACKEND}/{rota}", params=parametros)
        if resposta.status_code == 200:
            return resposta.json()
        st.warning(f"Alerta: O servidor retornou status {resposta.status_code} para a rota /{rota}.")
        return None
    except requests.exceptions.RequestException:
        st.error("Falha de comunicação. Verifique se o servidor Uvicorn está em execução.")
        return None


aba_visao, aba_base_mun, aba_prioridades = st.tabs([
    "📊 Visão Estratégica", 
    "🏢 Base de Municípios", 
    "📋 Controle de Prioridades"
])

# ==================== ABA 1: VISÃO ESTRATÉGICA ====================
with aba_visao:
    metricas_kpi = get_dados_brutos_api("kpis")
    if metricas_kpi:
        
        with st.container():
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Cidades Registradas", f"{metricas_kpi['total_municipios']:,}".replace(",", "."))
            k2.metric("Unidades Federativas", metricas_kpi['total_estados'])
            k3.metric(f"Habitantes ({metricas_kpi['ano_referencia']})", f"{int(metricas_kpi['populacao_total']):,}".replace(",", "."))
            k4.metric("Maior Concentração", metricas_kpi['municipio_mais_populoso'], f"{int(metricas_kpi['populacao_mais_populoso']):,}".replace(",", ".") + " hab")
        
        st.divider()

    
    col_ranking, col_proporcao = st.columns([6, 4])

    with col_ranking:
        st.markdown("#### Ranking de Cidades Mais Populosas")
        limite_busca = st.number_input("Tamanho do Ranking (N):", min_value=5, max_value=50, value=10, step=5)
        raw_ranking = get_dados_brutos_api("top-municipios", parametros={"n": limite_busca})
        
        if raw_ranking:
            df_ranking = pd.DataFrame(raw_ranking).sort_values(by="populacao", ascending=True)
            # Gráfico estilizado com template e paleta de cores diferente
            grafico_barras = px.bar(
                df_ranking, x="populacao", y="nome_municipio", color="sigla_uf", 
                orientation='h', template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            grafico_barras.update_layout(xaxis_title="Volume Populacional", yaxis_title="", showlegend=False)
            st.plotly_chart(grafico_barras, use_container_width=True)

    with col_proporcao:
        st.markdown("#### Proporção por Região")
        raw_regioes = get_dados_brutos_api("populacao-regiao")
        if raw_regioes:
            df_regioes = pd.DataFrame(raw_regioes)
            grafico_rosca = px.pie(
                df_regioes, values="populacao_total", names="nome_regiao", 
                hole=0.5, template="plotly_white"
            )
            st.plotly_chart(grafico_rosca, use_container_width=True)

    st.divider()
    
    col_estado, col_hist = st.columns(2)

    with col_estado:
        st.markdown("#### População Total por Estado")
        opcoes_regiao = ["Sem Filtro", "1 - Norte", "2 - Nordeste", "3 - Sudeste", "4 - Sul", "5 - Centro-Oeste"]
        filtro_reg = st.selectbox("Isolar Região Específica:", opcoes_regiao)
        
        id_regiao = int(filtro_reg.split(" - ")[0]) if filtro_reg != "Sem Filtro" else None
        raw_estados = get_dados_brutos_api("populacao-estado", parametros={"regiao_id": id_regiao} if id_regiao else None)
        
        if raw_estados:
            df_estados = pd.DataFrame(raw_estados)
            grafico_estados = px.bar(
                df_estados, x="sigla_uf", y="populacao_total", 
                color="sigla_uf", template="plotly_white"
            )
            grafico_estados.update_layout(xaxis_title="Estado", yaxis_title="População", showlegend=False)
            st.plotly_chart(grafico_estados, use_container_width=True)

    with col_hist:
        st.markdown("#### Frequência de Distribuição (Log)")
        raw_dist = get_dados_brutos_api("distribuicao-populacao")
        if raw_dist:
            grafico_hist = px.histogram(
                raw_dist, nbins=40, log_y=True, template="plotly_white",
                color_discrete_sequence=['#2E91E5']
            )
            grafico_hist.update_layout(xaxis_title="Habitantes", yaxis_title="Qtd. Cidades", showlegend=False)
            st.plotly_chart(grafico_hist, use_container_width=True)

    st.divider()
    
    col_scatter, col_matriz = st.columns([5, 5])

    with col_scatter:
        st.markdown("#### Dispersão: Volume de Cidades x Média Habitacional")
        raw_dispersao = get_dados_brutos_api("dispersao-estado")
        if raw_dispersao:
            df_dispersao = pd.DataFrame(raw_dispersao)
            grafico_dispersao = px.scatter(
                df_dispersao, x="qtd_municipios", y="populacao_media", 
                color="nome_regiao", text="sigla_uf", size_max=10, template="plotly_white"
            )
            st.plotly_chart(grafico_dispersao, use_container_width=True)

    with col_matriz:
        st.markdown("#### Matriz de Concentração: Região vs. Porte")
        raw_matriz = get_dados_brutos_api("heatmap-porte")
        if raw_matriz:
            df_matriz = pd.DataFrame(raw_matriz)
            df_pivotado = df_matriz.pivot(index="nome_regiao", columns="porte", values="quantidade").fillna(0)
            grafico_calor = px.imshow(
                df_pivotado, text_auto=True, aspect="auto", 
                color_continuous_scale="Blues"
            )
            st.plotly_chart(grafico_calor, use_container_width=True)


# ==================== ABA 2: BASE DE MUNICÍPIOS ====================
with aba_base_mun:
    st.markdown("### Operações na Base de Dados (CRUD)")
    tipo_operacao = st.radio("Selecione a Operação:", ["Inserir Registro", "Modificar Registro", "Excluir Registro"], horizontal=True)

    if tipo_operacao == "Inserir Registro":
        with st.form("form_insercao"):
            novo_nome = st.text_input("Nomenclatura Oficial:")
            novo_uf = st.number_input("Código IBGE do Estado (UF):", min_value=1, value=33) # Padrão RJ
            nova_pop = st.number_input("Censo/Estimativa Populacional:", min_value=0, value=50000)
            
            if st.form_submit_button("Efetivar Inserção"):
                resposta = requests.post(f"{URL_BACKEND}/municipios", json={"nome_municipio": novo_nome, "id_uf": novo_uf, "populacao": nova_pop})
                if resposta.status_code == 201:
                    st.success(f"Operação concluída! Identificador gerado: {resposta.json()['id_municipio']}")
                else:
                    st.error("Falha ao gravar no banco de dados.")

    elif tipo_operacao == "Modificar Registro":
        id_alvo = st.number_input("ID do Município Alvo:", min_value=1, step=1)
        upd_nome = st.text_input("Atualizar Nome (deixe em branco para ignorar):")
        upd_uf = st.number_input("Atualizar Código UF (0 para ignorar):", min_value=0, value=0)
        upd_pop = st.number_input("Atualizar População (-1 para ignorar):", min_value=-1, value=-1)
        
        if st.button("Executar Atualização"):
            carga_dados = {}
            if upd_nome: carga_dados["nome_municipio"] = upd_nome
            if upd_uf > 0: carga_dados["id_uf"] = upd_uf
            if upd_pop >= 0: carga_dados["populacao"] = upd_pop
            
            resposta = requests.put(f"{URL_BACKEND}/municipios/{id_alvo}", json=carga_dados)
            if resposta.status_code == 200:
                st.success("Atualização persistida com sucesso!")
            else:
                st.error("Não foi possível realizar a atualização.")

    elif tipo_operacao == "Excluir Registro":
        id_exclusao = st.number_input("Informe o ID a ser deletado:", min_value=1, step=1)
        if st.button("Confirmar Exclusão", type="primary"):
            resposta = requests.delete(f"{URL_BACKEND}/municipios/{id_exclusao}")
            if resposta.status_code == 200:
                st.warning("Registro excluído permanentemente.")
            else:
                st.error("Erro durante o processo de exclusão.")

# ==================== ABA 3: CONTROLE DE PRIORIDADES ====================
with aba_prioridades:
    st.markdown("### Lançamento e Edição de Acompanhamentos")
    
    # Abas internas para separar Criação/Edição e Exclusão
    tab_form_anot, tab_lista_anot = st.tabs(["Gerenciar Anotações", "Visualizar e Descartar"])
    
    with tab_form_anot:
        acao_gestor = st.radio("Selecione a ação:", ["Lançar Nova Anotação", "Editar Anotação Existente"], horizontal=True)
        
        with st.form("form_controle"):
            c_id, c_status, c_prio = st.columns(3)
            
            if acao_gestor == "Lançar Nova Anotação":
                id_alvo_gestao = c_id.number_input("Identificador do Município:", min_value=1, step=1)
            else:
                id_alvo_gestao = c_id.number_input("ID da Anotação a Editar:", min_value=1, step=1)
                
            status_gestao = c_status.selectbox("Situação Atual:", ["Sob Análise", "Alerta", "Encerrado", "Standby"])
            prio_gestao = c_prio.select_slider("Grau de Prioridade:", options=["Muito Baixa", "Baixa", "Média", "Alta", "Crítica"])
            
            resp_gestao = st.text_input("Analista Responsável:")
            obs_gestao = st.text_area("Detalhamento Técnico:")
            
            botao_submit = st.form_submit_button("Efetivar Operação")
            
            if botao_submit:
                carga = {
                    "status": status_gestao,
                    "prioridade": prio_gestao,
                    "responsavel": resp_gestao,
                    "observacao": obs_gestao
                }
                
                if acao_gestor == "Lançar Nova Anotação":
                    carga["id_municipio"] = id_alvo_gestao
                    resposta = requests.post(f"{URL_BACKEND}/anotacoes", json=carga)
                    if resposta.status_code == 201:
                        st.success("Lançamento registrado no controle.")
                    else:
                        st.error("Falha ao registrar lançamento.")
                else:
                    # Rota PUT para atualizar a anotação existente
                    resposta = requests.put(f"{URL_BACKEND}/anotacoes/{id_alvo_gestao}", json=carga)
                    if resposta.status_code == 200:
                        st.success("Anotação modificada com sucesso.")
                    else:
                        st.error("Falha ao editar a anotação.")

    with tab_lista_anot:
        st.markdown("### Tabela de Registros Ativos")
        raw_anotacoes = get_dados_brutos_api("anotacoes")
        
        if raw_anotacoes:
            st.dataframe(pd.DataFrame(raw_anotacoes), use_container_width=True)
            
            st.divider()
            st.markdown("#### Remover Lançamento")
            col_del, _ = st.columns(2)
            with col_del:
                id_limpeza = st.number_input("ID da Anotação a ser descartada:", min_value=1, step=1)
                if st.button("Descartar Registro"):
                    resposta = requests.delete(f"{URL_BACKEND}/anotacoes/{id_limpeza}")
                    if resposta.status_code == 200:
                        st.success("Registro descartado.")
                    else:
                        st.error("Erro ao tentar limpar o registro.")