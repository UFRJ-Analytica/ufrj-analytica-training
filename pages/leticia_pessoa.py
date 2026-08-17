"""
Tela de acompanhamento populacional - Leticia Pessoa

Duas áreas:
- Análise: KPIs, top N, pizza por região, barras por estado, histograma,
  dispersão município x estado, heatmap região x porte.
- Cadastro: CRUD dos dados básicos do município (nome/estado/população)
  e CRUD das anotações do gestor (status, prioridade, observação...).

Toda comunicação com os dados passa pela API via requests - nenhuma
conexão direta com o banco acontece aqui.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000/leticia-pessoa"

st.set_page_config(page_title="Acompanhamento populacional", layout="wide")
st.title("Painel de acompanhamento populacional")


# ---------------------------------------------------------------------------
# Funções auxiliares de chamada à API
# ---------------------------------------------------------------------------

def api_get(caminho: str, params: dict | None = None):
    """GET genérico. Retorna o JSON da resposta, ou None se a API falhar."""
    try:
        resposta = requests.get(f"{API_URL}{caminho}", params=params, timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        st.error(f"Não foi possível conectar à API ({caminho}). Detalhe: {erro}")
        return None


def api_post(caminho: str, dados: dict):
    try:
        resposta = requests.post(f"{API_URL}{caminho}", json=dados, timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        st.error(f"Erro ao criar registro ({caminho}). Detalhe: {erro}")
        return None


def api_put(caminho: str, dados: dict):
    try:
        resposta = requests.put(f"{API_URL}{caminho}", json=dados, timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        st.error(f"Erro ao atualizar registro ({caminho}). Detalhe: {erro}")
        return None


def api_delete(caminho: str):
    try:
        resposta = requests.delete(f"{API_URL}{caminho}", timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        st.error(f"Erro ao remover registro ({caminho}). Detalhe: {erro}")
        return None


# ---------------------------------------------------------------------------
# Abas principais
# ---------------------------------------------------------------------------

aba_analise, aba_cadastro = st.tabs(["📊 Análise", "📝 Cadastro"])


# ---------------------------------------------------------------------------
# ABA DE ANÁLISE
# ---------------------------------------------------------------------------

with aba_analise:

    # --- KPIs -----------------------------------------------------------
    st.subheader("Resumo geral")
    kpis = api_get("/estatisticas/resumo")

    if kpis:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de municípios", f"{kpis['total_municipios']:,}")
        col2.metric("Total de estados", kpis["total_estados"])
        col3.metric("Ano de referência", kpis["ano_referencia"])

        col4, col5 = st.columns(2)
        col4.metric("População total", f"{kpis['populacao_total']:,}")
        col5.metric("Município mais populoso", kpis["municipio_mais_populoso"])

    st.divider()

    # --- Top N municípios -------------------------------------------------
    st.subheader("Top municípios mais populosos")
    n = st.slider("Quantidade de municípios", min_value=3, max_value=50, value=10)

    top_municipios = api_get("/populacao/top_municipios", params={"n": n})

    if top_municipios:
        df_top = pd.DataFrame(top_municipios)

        col_tabela, col_grafico = st.columns([1, 2])
        with col_tabela:
            st.dataframe(df_top, hide_index=True, use_container_width=True)
        with col_grafico:
            fig_top = px.bar(
                df_top.sort_values("populacao"),
                x="populacao", y="nome", orientation="h",
                labels={"populacao": "População", "nome": "Município"},
            )
            st.plotly_chart(fig_top, use_container_width=True)

    st.divider()

    # --- População por região e por estado, lado a lado -------------------
    col_regiao, col_estado = st.columns(2)

    with col_regiao:
        st.subheader("População por região")
        pop_regiao = api_get("/populacao/por-regiao")
        if pop_regiao:
            df_regiao = pd.DataFrame(pop_regiao)
            fig_regiao = px.pie(
                df_regiao, names="regiao", values="populacao", hole=0.4
            )
            st.plotly_chart(fig_regiao, use_container_width=True)

    with col_estado:
        st.subheader("População por estado")

        opcoes_regiao = ["Todas"]
        if pop_regiao:
            opcoes_regiao += [item["regiao"] for item in pop_regiao]

        regiao_filtro = st.selectbox("Filtrar por região", opcoes_regiao)
        params_estado = None if regiao_filtro == "Todas" else {"regiao": regiao_filtro}

        pop_estado = api_get("/populacao/por-uf", params=params_estado)
        if pop_estado:
            df_estado = pd.DataFrame(pop_estado)
            fig_estado = px.bar(
                df_estado.sort_values("populacao", ascending=False),
                x="estado", y="populacao",
            )
            st.plotly_chart(fig_estado, use_container_width=True)

    st.divider()

    # --- Distribuição da população (histograma) ----------------------------
    st.subheader("Distribuição da população dos municípios")
    distribuicao = api_get("/populacao/municipio")
    if distribuicao:
        df_dist = pd.DataFrame(distribuicao)
        fig_hist = px.histogram(df_dist, x="populacao", nbins=50)
        fig_hist.update_layout(
            xaxis_title="População do município",
            yaxis_title="Quantidade de municípios",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()

    # --- Dispersão município x estado ---------------------------------------
    st.subheader("Municípios x população média por estado")
    dispersao = api_get("/populacao/dispersao-uf")
    if dispersao:
        df_disp = pd.DataFrame(dispersao)
        fig_disp = px.scatter(
            df_disp,
            x="quantidade_municipios", y="populacao_media",
            color="regiao", hover_name="estado",
            labels={
                "quantidade_municipios": "Quantidade de municípios",
                "populacao_media": "População média",
            },
        )
        st.plotly_chart(fig_disp, use_container_width=True)

    st.divider()

    # --- Heatmap região x porte ---------------------------------------------
    st.subheader("Mapa de calor: região x porte do município")
    heatmap_dados = api_get("/populacao/heatmap-regiao-porte")
    if heatmap_dados:
        df_heat = pd.DataFrame(heatmap_dados)
        tabela_pivot = df_heat.pivot_table(
            index="regiao", columns="porte", values="quantidade", fill_value=0
        )
        fig_heat = px.imshow(
            tabela_pivot,
            text_auto=True,
            labels=dict(x="Porte", y="Região", color="Quantidade"),
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_heat, use_container_width=True)


# ---------------------------------------------------------------------------
# ABA DE CADASTRO
# ---------------------------------------------------------------------------

with aba_cadastro:

    sub_municipio, sub_anotacoes = st.tabs(
        ["Dados do município", "Anotações do gestor"]
    )

    # --- Dados básicos do município (criar / editar) ------------------------
    with sub_municipio:
        st.subheader("Cadastrar novo município")

        with st.form("form_novo_municipio", clear_on_submit=True):
            nome_novo = st.text_input("Nome do município")
            uf_novo = st.number_input("Código do estado (id_uf)", min_value=1, step=1)
            populacao_novo = st.number_input("População", min_value=0, step=1)
            enviado_criar = st.form_submit_button("Criar município")

        if enviado_criar:
            if nome_novo.strip():
                resultado = api_post(
                    "/municipios",
                    {
                        "nome_municipio": nome_novo,
                        "id_uf": int(uf_novo),
                        "populacao": int(populacao_novo),
                    },
                )
                if resultado:
                    st.success(
                        f"Município '{resultado['nome_municipio']}' criado "
                        f"com id {resultado['id_municipio']}."
                    )
            else:
                st.warning("Informe o nome do município.")

        st.divider()
        st.subheader("Editar ou remover município existente")

        lista_municipios = api_get("/municipios")

        if lista_municipios:
            df_municipios = pd.DataFrame(lista_municipios)
            opcoes = {
                f"{row['nome_municipio']} (id {row['id_municipio']})": row["id_municipio"]
                for _, row in df_municipios.iterrows()
            }
            escolha = st.selectbox("Selecione um município", list(opcoes.keys()))
            id_selecionado = opcoes[escolha]

            municipio_atual = api_get(f"/municipios/{id_selecionado}")

            if municipio_atual:
                with st.form("form_editar_municipio"):
                    nome_edit = st.text_input(
                        "Nome", value=municipio_atual["nome_municipio"]
                    )
                    uf_edit = st.number_input(
                        "Código do estado (id_uf)",
                        min_value=1, step=1,
                        value=int(municipio_atual["id_uf"]),
                    )
                    populacao_edit = st.number_input(
                        "População",
                        min_value=0, step=1,
                        value=int(municipio_atual["populacao"]),
                    )
                    col_salvar, col_remover = st.columns(2)
                    salvar = col_salvar.form_submit_button("Salvar alterações")
                    remover = col_remover.form_submit_button("Remover município")

                if salvar:
                    resultado = api_put(
                        f"/municipios/{id_selecionado}",
                        {
                            "nome_municipio": nome_edit,
                            "id_uf": int(uf_edit),
                            "populacao": int(populacao_edit),
                        },
                    )
                    if resultado:
                        st.success("Município atualizado.")
                        st.rerun()

                if remover:
                    resultado = api_delete(f"/municipios/{id_selecionado}")
                    if resultado:
                        st.success("Município removido.")
                        st.rerun()

    # --- Anotações do gestor (cadastro) --------------------------------------
    with sub_anotacoes:
        st.subheader("Nova anotação")

        lista_municipios_anot = api_get("/municipios")

        if lista_municipios_anot:
            opcoes_anot = {
                f"{row['nome_municipio']} (id {row['id_municipio']})": row["id_municipio"]
                for row in lista_municipios_anot
            }

            with st.form("form_nova_anotacao", clear_on_submit=True):
                municipio_escolhido = st.selectbox(
                    "Município", list(opcoes_anot.keys())
                )
                status_novo = st.selectbox(
                    "Status", ["prioridade", "em observação", "normal"]
                )
                prioridade_novo = st.selectbox("Prioridade", ["baixa", "média", "alta"])
                observacao_novo = st.text_area("Observação")
                responsavel_novo = st.text_input("Responsável")
                enviado_anotacao = st.form_submit_button("Salvar anotação")

            if enviado_anotacao:
                resultado = api_post(
                    "/cadastro",
                    {
                        "id_municipio": opcoes_anot[municipio_escolhido],
                        "status": status_novo,
                        "prioridade": prioridade_novo,
                        "observacao": observacao_novo,
                        "responsavel": responsavel_novo,
                    },
                )
                if resultado:
                    st.success("Anotação criada.")
                    st.rerun()

        st.divider()
        st.subheader("Anotações existentes")

        anotacoes = api_get("/cadastro")

        if anotacoes:
            for anotacao in anotacoes:
                with st.expander(
                    f"Cadastro #{anotacao['id_cadastro']} "
                    f"— município {anotacao['id_municipio']} "
                    f"— {anotacao['status'] or 'sem status'}"
                ):
                    with st.form(f"form_editar_anotacao_{anotacao['id_cadastro']}"):
                        status_edit = st.selectbox(
                            "Status",
                            ["prioridade", "em observação", "normal"],
                            index=["prioridade", "em observação", "normal"].index(
                                anotacao["status"]
                            ) if anotacao["status"] in
                            ["prioridade", "em observação", "normal"] else 0,
                        )
                        prioridade_edit = st.selectbox(
                            "Prioridade",
                            ["baixa", "média", "alta"],
                            index=["baixa", "média", "alta"].index(
                                anotacao["prioridade"]
                            ) if anotacao["prioridade"] in
                            ["baixa", "média", "alta"] else 0,
                        )
                        observacao_edit = st.text_area(
                            "Observação", value=anotacao["observacao"] or ""
                        )
                        responsavel_edit = st.text_input(
                            "Responsável", value=anotacao["responsavel"] or ""
                        )

                        col_salvar_a, col_remover_a = st.columns(2)
                        salvar_a = col_salvar_a.form_submit_button("Salvar")
                        remover_a = col_remover_a.form_submit_button("Remover")

                    if salvar_a:
                        resultado = api_put(
                            f"/cadastro/{anotacao['id_cadastro']}",
                            {
                                "status": status_edit,
                                "prioridade": prioridade_edit,
                                "observacao": observacao_edit,
                                "responsavel": responsavel_edit,
                            },
                        )
                        if resultado:
                            st.success("Anotação atualizada.")
                            st.rerun()

                    if remover_a:
                        resultado = api_delete(f"/cadastro/{anotacao['id_cadastro']}")
                        if resultado:
                            st.success("Anotação removida.")
                            st.rerun()
        else:
            st.info("Nenhuma anotação cadastrada ainda.")