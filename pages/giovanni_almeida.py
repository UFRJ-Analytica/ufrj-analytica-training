import requests
from requests.exceptions import RequestException
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
BASE_URL = "http://127.0.0.1:8000/giovanni-almeida"

def _fazer_requisicao(metodo: str, endpoint: str, payload: dict = None, params: dict = None) -> dict | list | None:
    """
    Função universal para lidar com o tráfego HTTP.
    - payload: mapeado para o Request Body (usado em POST, PUT).
    - params: mapeado para a Query String da URL (usado em GET, DELETE).
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.request(method=metodo, url=url, json=payload, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except RequestException as e:
        print(f"Falha na comunicação com a API em {url}: {str(e)}")
        return None



def obter_kpis():
    return _fazer_requisicao("GET", "/estatisticas/resumo")

def obter_municipios(limit: int):
    return _fazer_requisicao("GET", "/populacao/top-municipios", params={"limit": limit})

def pop_regiao():
    return _fazer_requisicao("GET", "/populacao/por-regiao")

def pop_uf(id_regiao: int | None = None):
    parametros = {"id_regiao": id_regiao} if id_regiao is not None else None
    return _fazer_requisicao("GET", "/populacao/por-uf", params=parametros)

def pop_mun():
    return _fazer_requisicao("GET", "/populacao/distribuicao")

def scatter_mun_popmedia():
    return _fazer_requisicao("GET", "/populacao/dispersao-uf")

def heatmap_reg_porte():
    return _fazer_requisicao("GET", "/populacao/heatmap-regiao-porte")

def obter_registros_gestor(id_municipio: int):
    return _fazer_requisicao("GET", f"/municipios/{id_municipio}/registros")

def buscar_municipio_por_nome(nome: str):
    return _fazer_requisicao("GET", "/municipios/namesearch", params={"nome_municipio": nome})

def buscar_municipio_por_id(id_mun: int):
    return _fazer_requisicao("GET", f"/municipios/{id_mun}")

# --- Métodos de Mutação (Corpo da requisição via 'payload') ---

def criar_municipio(dados_municipio: dict):
    return _fazer_requisicao("POST", "/municipios", payload=dados_municipio)

def atualizar_municipio(id_municipio: int, dados_municipio: dict):
    return _fazer_requisicao("PUT", f"/municipios/{id_municipio}", payload=dados_municipio)

def remover_municipio(id_municipio: int):
    return _fazer_requisicao("DELETE", f"/municipios/{id_municipio}")

def criar_registros_gestor(id_municipio: int, payload_registro: dict):
    return _fazer_requisicao("POST", f"/municipios/{id_municipio}/registros", payload=payload_registro)

def deletar_registros_gestor(id_registro: int):
    return _fazer_requisicao("DELETE", f"/registros/{id_registro}")


st.set_page_config(page_title="Dashboard de Municípios", layout="wide")

kpis = obter_kpis()
if kpis is None:
    st.error("A API está indisponível no momento. Comunicação rompida.")
    st.stop()

st.title("Sistema de Gestão de Municípios")
tab_analise, tab_cadastro = st.tabs(["📊 Área de Análise", "📝 Área de Cadastro"])

# ==========================================
# ÁREA DE ANÁLISE
# ==========================================
with tab_analise:
    st.header("Visão Geral")
    
    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total de Municípios", kpis.get("numero_municipios", 0))
    with col2:
        st.metric("Total de Estados", kpis.get("numero_estados", 0))
    with col3:
        st.metric("População Total", f"{kpis.get('populacao_total', 0):,}".replace(",", "."))
    with col4:
        st.metric("Mais Populoso", kpis.get("municipio_mais_populoso", "N/D"))
    with col5:
        # Pendência na API: O endpoint de KPIs não retorna o ano de referência
        st.metric("Ano de Referência", kpis.get("ano_ref", "N/D")) 

    st.divider()

    #Filtros Interativos (Sidebar)
    st.sidebar.header("Filtros Interativos")
    top_n = st.sidebar.number_input("Quantidade (Top N):", min_value=5, max_value=100, value=10, step=5)
    
    # Busca regiões para o filtro de UF
    regioes_db = _fazer_requisicao("GET", "/regioes") # Uso direto para filtro
    opcoes_regiao = {"Todas": None}
    if regioes_db:
        for r in regioes_db:
            opcoes_regiao[r["nome_regiao"]] = r["id_regiao"]
            
    regiao_selecionada = st.sidebar.selectbox("Filtrar Estado por Região:", options=list(opcoes_regiao.keys()))
    id_regiao_param = opcoes_regiao[regiao_selecionada]

    # Gráficos
    
    # Top N Municípios (Tabela e Gráfico)
    st.subheader(f"Top {top_n} Municípios Mais Populosos")
    dados_top = obter_municipios(limit=top_n)
    if dados_top:
        df_top = pd.DataFrame(dados_top).sort_values(by="valor_populacao", ascending=True)
        col_tabela, col_grafico = st.columns([1, 2])
        
        with col_tabela:
            st.dataframe(df_top.sort_values(by="valor_populacao", ascending=False).reset_index(drop=True), use_container_width=True)
            
        with col_grafico:
            fig_top, ax_top = plt.subplots(figsize=(8, 4))
            ax_top.barh(df_top["nome_municipio"], df_top["valor_populacao"], color="#1f77b4")
            ax_top.set_xlabel("População")
            plt.tight_layout()
            st.pyplot(fig_top)

    st.divider()
    col_grafico_1, col_grafico_2 = st.columns(2)

    # População por Região (Pizza)
    with col_grafico_1:
        st.subheader("População por Região")
        dados_regiao = pop_regiao()
        if dados_regiao:
            df_reg = pd.DataFrame(dados_regiao)
            fig_reg, ax_reg = plt.subplots(figsize=(6, 4))
            ax_reg.pie(df_reg["valor_populacao"], labels=df_reg["nome_regiao"], autopct="%1.1f%%", startangle=90)
            ax_reg.axis("equal")
            st.pyplot(fig_reg)

    # População por Estado (Barras)
    with col_grafico_2:
        st.subheader("População por Estado" + (f" ({regiao_selecionada})" if id_regiao_param else ""))
        dados_uf = pop_uf(id_regiao=id_regiao_param)
        if dados_uf:
            df_uf = pd.DataFrame(dados_uf).sort_values(by="valor_populacao", ascending=False)
            fig_uf, ax_uf = plt.subplots(figsize=(6, 4))
            ax_uf.bar(df_uf["nome_uf"], df_uf["valor_populacao"], color="#ff7f0e")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_uf)

    col_grafico_3, col_grafico_4 = st.columns(2)

    # Distribuição da População (Histograma)
    with col_grafico_3:
        st.subheader("Distribuição da População (Todos)")
        dados_mun = pop_mun()
        if dados_mun:
            df_mun = pd.DataFrame(dados_mun)
            fig_hist, ax_hist = plt.subplots(figsize=(6, 4))
            ax_hist.hist(df_mun["valor_populacao"], bins=50, color="#2ca02c", edgecolor="black", log=True)
            ax_hist.set_xlabel("População")
            ax_hist.set_ylabel("Frequência LOG")
            plt.tight_layout()
            st.pyplot(fig_hist)

    # Dispersão: Municípios x Pop Média (Scatter)
    with col_grafico_4:
        st.subheader("Dispersão: Municípios x População Média (UF)")
        dados_scatter = scatter_mun_popmedia()
        if dados_scatter:
            df_scatter = pd.DataFrame(dados_scatter)
            fig_scat, ax_scat = plt.subplots(figsize=(6, 4))
            # Falta 'nome_regiao' na API para colorir. por enquanto sem separação de cor.
            ax_scat.scatter(df_scatter["numero_municipios"], df_scatter["avg_populacao"], alpha=0.7)
            
            for i, row in df_scatter.iterrows():
                ax_scat.annotate(row["nome_uf"], (row["numero_municipios"], row["avg_populacao"]), fontsize=8)
                
            ax_scat.set_xlabel("Quantidade de Municípios")
            ax_scat.set_ylabel("População Média")
            plt.tight_layout()
            st.pyplot(fig_scat)

    # Mapa de Calor: Região x Porte
    st.subheader("Mapa de Calor: Região x Porte")
    dados_heatmap = heatmap_reg_porte()
    if dados_heatmap:
        df_heat = pd.DataFrame(dados_heatmap)
        matriz_heat = df_heat.pivot(index="nome_regiao", columns="nome_porte", values="numero_municipios").fillna(0)
        fig_heat, ax_heat = plt.subplots(figsize=(8, 3))
        sns.heatmap(matriz_heat, annot=True, fmt=".0f", cmap="Blues", ax=ax_heat)
        plt.tight_layout()
        st.pyplot(fig_heat)


# ==========================================
# ÁREA DE CADASTRO (CRUD)
# ==========================================
with tab_cadastro:
    st.header("Gerenciamento de Entidades")
    subtab_consulta, subtab_mun, subtab_gestor = st.tabs(["Consultar Municípios", "Ações em Municípios", "Anotações de Gestor"])
    
    with subtab_consulta:
        st.subheader("Busca de Informações")
        modo_busca = st.radio("Método de Busca:", ["Por Nome", "Por ID"], horizontal=True)
        
        if modo_busca == "Por Nome":
            nome_busca = st.text_input("Digite o nome exato do município:")
            if st.button("Buscar por Nome"):
                if nome_busca:
                    resultado = buscar_municipio_por_nome(nome_busca)
                    if resultado:
                        st.dataframe(pd.DataFrame(resultado), use_container_width=True)
                    else:
                        st.warning("Município não encontrado.")
        
        elif modo_busca == "Por ID":
            id_busca = st.number_input("Digite o ID do município:", min_value=1, step=1)
            if st.button("Buscar por ID"):
                resultado = buscar_municipio_por_id(id_busca)
                if resultado:
                    st.dataframe(pd.DataFrame(resultado), use_container_width=True)
                else:
                    st.warning("Município não encontrado.")    
    with subtab_mun:
        acao_mun = st.radio("Ação:", ["Criar Novo", "Atualizar", "Remover"], horizontal=True, key="acao_mun")
        
        if acao_mun == "Criar Novo":
            with st.form("form_criar_mun"):
                nome_mun = st.text_input("Nome do Município")
                nome_est = st.text_input("Nome do Estado (Ex: Rio de Janeiro)")
                pop_munic = st.number_input("População", min_value=1, step=1)
                
                if st.form_submit_button("Criar Município"):
                    res = criar_municipio({"nome_municipio": nome_mun, "nome_estado": nome_est, "populacao": pop_munic})
                    if res:
                        st.success("Município criado com sucesso!")
                        st.rerun()
        
        elif acao_mun in ["Atualizar", "Remover"]:
            id_mun = st.number_input("ID do Município Alvo", min_value=1, step=1)
            
            if acao_mun == "Atualizar":
                with st.form("form_atualizar_mun"):
                    novo_nome = st.text_input("Novo Nome (Deixe em branco para não alterar)")
                    novo_estado = st.text_input("Novo Estado (Deixe em branco para não alterar)")
                    nova_pop = st.number_input("Nova População (0 para não alterar)", min_value=0, step=1)
                    
                    if st.form_submit_button("Atualizar Município"):
                        payload = {}
                        if novo_nome: payload["novo_nome"] = novo_nome
                        if novo_estado: payload["novo_estado"] = novo_estado
                        if nova_pop > 0: payload["nova_pop"] = nova_pop
                        
                        # Note: Pela sua API, PUT de municípios recebe query params, não body. 
                        # O api_client precisaria estar adaptado para isso.
                        res = atualizar_municipio(id_municipio=id_mun,dados_municipio=payload)
                        if res:
                            st.success("Atualizado com sucesso!")
                            st.rerun()
            else:
                if st.button("Remover Município"):
                    res = remover_municipio(id_mun)
                    if res:
                        st.success("Removido com sucesso!")
                        st.rerun()

    with subtab_gestor:
        id_mun_gestor = st.number_input("ID do Município para Gestão", min_value=1, step=1, key="id_gestor")
        acao_gest = st.radio("Ação no Registro:", ["Listar/Remover", "Criar Novo", "Editar"], horizontal=True)
        
        if acao_gest == "Criar Novo":
            with st.form("form_criar_reg"):
                status = st.text_input("Status")
                prior = st.text_input("Prioridade")
                resp = st.text_input("Responsável")
                obs = st.text_area("Observação")
                
                if st.form_submit_button("Salvar Registro"):
                    payload = {"status": status, "prioridade": prior, "responsavel": resp, "observacao": obs}
                    if criar_registros_gestor(id_mun_gestor, payload):
                        st.success("Registro adicionado!")
                        st.rerun()
                        
        elif acao_gest == "Listar/Remover":
            registros = obter_registros_gestor(id_mun_gestor)
            if registros:
                st.dataframe(pd.DataFrame(registros), use_container_width=True)
                id_remover = st.number_input("ID do Registro para Remover", min_value=1, step=1)
                if st.button("Excluir Registro"):
                    if deletar_registros_gestor(id_remover):
                        st.success("Excluído com sucesso!")
                        st.rerun()
            else:
                st.info("Nenhum registro encontrado para este município.")
                
        elif acao_gest == "Editar":
            id_editar = st.number_input("ID do Registro para Editar", min_value=1, step=1)
            with st.form("form_editar_reg"):
                status = st.text_input("Novo Status")
                prior = st.text_input("Nova Prioridade")
                resp = st.text_input("Novo Responsável")
                obs = st.text_area("Nova Observação")
                
                if st.form_submit_button("Atualizar Registro"):
                    payload = {"status": status, "prioridade": prior, "responsavel": resp, "observacao": obs}
                    if _fazer_requisicao("PUT", f"/registros/{id_editar}", payload=payload):
                        st.success("Registro atualizado!")
                        st.rerun()