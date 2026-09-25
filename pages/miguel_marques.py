"""
Painel de acompanhamento populacional - Miguel Marques.

Duas áreas, conforme pedido na tarefa:
  1) Análise: KPIs, top N, pizza por região, barras por estado, histograma,
     dispersão por estado e heatmap região x porte.
  2) Cadastro: CRUD de município (dados básicos) e CRUD das anotações do
     gestor (informações que não vêm do IBGE).

Toda comunicação passa pela API via requests; se a API estiver fora do ar,
mostramos um aviso em vez de deixar a tela quebrar (nenhum acesso direto ao banco).
"""
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Painel Populacional - Miguel Marques", layout="wide")
st.title("Acompanhamento Populacional dos Municípios Brasileiros")

API_URL = "http://127.0.0.1:8000/miguel-marques"


# ---------------------------------------------------------------------------
# Acesso à API
# Cada função trata falhas de conexão e devolve None ou lista vazia para que a
# interface continue funcionando mesmo se a API estiver indisponível.
# ---------------------------------------------------------------------------
def _get(caminho: str, params: dict | None = None):
    try:
        resposta = requests.get(f"{API_URL}{caminho}", params=params, timeout=5)
        resposta.raise_for_status()
        return resposta.json()
    except (requests.exceptions.RequestException, ValueError):
        return None


def _extrair_erro(resposta):
    if resposta is None:
        return "A API está fora do ar."
    try:
        payload = resposta.json()
        return payload.get("detail", resposta.text or "Erro desconhecido")
    except ValueError:
        return resposta.text or "Erro desconhecido"


def buscar_kpis():
    return _get("/kpis")


def buscar_top_municipios(n: int):
    return _get("/municipios/top", {"n": n})


def buscar_populacao_regiao():
    return _get("/regioes/populacao")


def buscar_regioes_disponiveis():
    return _get("/regioes") or []


def buscar_populacao_estado(id_regiao: int | None):
    params = {"id_regiao": id_regiao} if id_regiao else None
    return _get("/estados/populacao", params)


def buscar_distribuicao():
    return _get("/municipios/distribuicao")


def buscar_dispersao():
    return _get("/estados/dispersao")


def buscar_heatmap():
    return _get("/municipios/heatmap")


def listar_acompanhamentos(id_municipio: int | None = None):
    params = {"id_municipio": id_municipio} if id_municipio else None
    resultado = _get("/acompanhamentos", params)
    return resultado or []


# CRUD de município: envia os dados para a API e devolve a resposta do backend
# para que a interface possa mostrar mensagens claras de sucesso ou erro.
def criar_municipio(nome: str, id_uf: int, populacao: int):
    try:
        return requests.post(
            f"{API_URL}/municipios",
            json={"nome_municipio": nome, "id_uf": id_uf, "populacao": populacao},
            timeout=5,
        )
    except requests.exceptions.RequestException:
        return None


def atualizar_municipio(id_municipio: int, nome: str, id_uf: int, populacao: int):
    try:
        return requests.put(
            f"{API_URL}/municipios/{id_municipio}",
            json={"nome_municipio": nome, "id_uf": id_uf, "populacao": populacao},
            timeout=5,
        )
    except requests.exceptions.RequestException:
        return None


def deletar_municipio(id_municipio: int):
    try:
        return requests.delete(f"{API_URL}/municipios/{id_municipio}", timeout=5)
    except requests.exceptions.RequestException:
        return None


# As anotações do gestor complementam os dados do IBGE e ajudam a registrar
# observações, prioridade e responsável por município.
def criar_acompanhamento(id_municipio, status, prioridade, observacao, responsavel):
    payload = {
        "id_municipio": id_municipio,
        "status": status,
        "prioridade": prioridade,
        "observacao": observacao,
        "responsavel": responsavel,
    }
    try:
        return requests.post(f"{API_URL}/acompanhamentos", json=payload, timeout=5)
    except requests.exceptions.RequestException:
        return None


def atualizar_acompanhamento(id_acompanhamento, status, prioridade, observacao, responsavel):
    payload = {
        "status": status,
        "prioridade": prioridade,
        "observacao": observacao,
        "responsavel": responsavel,
    }
    try:
        return requests.put(f"{API_URL}/acompanhamentos/{id_acompanhamento}", json=payload, timeout=5)
    except requests.exceptions.RequestException:
        return None


def deletar_acompanhamento(id_acompanhamento):
    try:
        return requests.delete(f"{API_URL}/acompanhamentos/{id_acompanhamento}", timeout=5)
    except requests.exceptions.RequestException:
        return None


# Seção de análise
st.header("Análise geral")

kpis = buscar_kpis()

if kpis is None:
    st.error("A API está fora do ar. Verifique se o servidor Uvicorn está rodando.")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de municípios", kpis["total_municipios"])
    col2.metric("Total de estados", kpis["total_estados"])
    pop_formatada = f"{kpis['populacao_total']:,}".replace(",", ".")
    col3.metric("População total", pop_formatada)
    col4.metric("Ano de referência", kpis["ano_referencia"])
    mais_populoso = kpis["municipio_mais_populoso"]
    if mais_populoso:
        col5.metric(
            "Mais populoso",
            f"{mais_populoso['municipio']} ({mais_populoso['uf']})",
            f"{mais_populoso['populacao']:,}".replace(",", "."),
        )

st.divider()
st.subheader("Visualizações")

col_top, col_regiao = st.columns(2)

with col_top:
    st.markdown("### Municípios mais populosos")
    n_selecionado = st.slider("Quantidade de municípios", min_value=5, max_value=50, value=10, step=5)
    dados_top = buscar_top_municipios(n_selecionado)
    if dados_top:
        df_top = pd.DataFrame(dados_top)
        st.dataframe(df_top, use_container_width=True, hide_index=True)
        fig_top = px.bar(df_top, x="nome_municipio", y="populacao", color="uf")
        st.plotly_chart(fig_top, use_container_width=True)

with col_regiao:
    st.markdown("### População por região")
    dados_regiao = buscar_populacao_regiao()
    if dados_regiao:
        df_regiao = pd.DataFrame(dados_regiao)
        fig_donut = px.pie(df_regiao, values="populacao_total", names="nome_regiao", hole=0.4)
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_donut, use_container_width=True)

st.divider()
col_estado, col_hist = st.columns(2)

with col_estado:
    st.markdown("### População por estado")
    regioes = buscar_regioes_disponiveis()
    opcoes = {"Todas": None}
    opcoes.update({r["nome_regiao"]: r["id_regiao"] for r in regioes})
    regiao_selecionada = st.selectbox("Filtrar por região", list(opcoes.keys()))
    dados_estado = buscar_populacao_estado(opcoes[regiao_selecionada])
    if dados_estado:
        df_estado = pd.DataFrame(dados_estado)
        fig_barras = px.bar(
            df_estado, x="sigla_uf", y="populacao_total",
            labels={"sigla_uf": "Estado", "populacao_total": "População"},
        )
        st.plotly_chart(fig_barras, use_container_width=True)

with col_hist:
    st.markdown("### Distribuição da população")
    dados_dist = buscar_distribuicao()
    if dados_dist:
        df_dist = pd.DataFrame({"populacao": dados_dist})
        fig_hist = px.histogram(df_dist, x="populacao", nbins=50, labels={"populacao": "População do município"})
        st.plotly_chart(fig_hist, use_container_width=True)

st.divider()
col_scatter, col_heat = st.columns(2)

with col_scatter:
    st.markdown("### Dispersão: municípios x população média por estado")
    dados_disp = buscar_dispersao()
    if dados_disp:
        df_disp = pd.DataFrame(dados_disp)
        fig_scatter = px.scatter(
            df_disp, x="qtd_municipios", y="populacao_media",
            color="nome_regiao", hover_name="sigla_uf",
            labels={"qtd_municipios": "Qtd. de municípios", "populacao_media": "População média", "nome_regiao": "Região"},
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with col_heat:
    st.markdown("### Mapa de calor: região x porte")
    dados_heat = buscar_heatmap()
    if dados_heat:
        df_heat = pd.DataFrame(dados_heat)
        fig_heat = px.density_heatmap(
            df_heat, x="porte", y="nome_regiao", z="quantidade",
            histfunc="sum", color_continuous_scale="Viridis", text_auto=True,
            labels={"porte": "Porte", "nome_regiao": "Região", "quantidade": "Quantidade"},
        )
        fig_heat.update_xaxes(categoryorder="array", categoryarray=["Pequeno", "Médio", "Grande"])
        st.plotly_chart(fig_heat, use_container_width=True)


# Seção de cadastro

st.divider()
st.header("Gestão e cadastro")

tab_mun, tab_gestor = st.tabs(["Municípios", "Anotações do gestor"])

with tab_mun:
    col_criar, col_editar = st.columns(2)

    with col_criar:
        st.subheader("Cadastrar município")
        with st.form("form_criar_mun"):
            nome_novo = st.text_input("Nome do município")
            uf_novo = st.number_input("ID do estado (id_uf)", min_value=11, max_value=53, step=1)
            pop_nova = st.number_input("População estimada", min_value=0, step=1)
            if st.form_submit_button("Cadastrar"):
                if not nome_novo.strip():
                    st.error("Informe um nome válido para o município.")
                else:
                    res = criar_municipio(nome_novo.strip(), int(uf_novo), int(pop_nova))
                    if res is None:
                        st.error("A API está fora do ar. Não foi possível cadastrar o município.")
                    elif res.status_code == 201:
                        payload = res.json()
                        st.success(f"Município criado! ID gerado: {payload['id_municipio']}")
                    else:
                        st.error(f"Erro ao criar município: {_extrair_erro(res)}")

    with col_editar:
        st.subheader("Atualizar ou remover município")
        id_alvo = st.number_input("ID do município alvo", min_value=1, step=1)
        with st.form("form_atualizar_mun"):
            st.markdown("**Novos dados (para atualização):**")
            nome_edit = st.text_input("Novo nome")
            uf_edit = st.number_input("Novo id_uf", min_value=11, max_value=53, step=1)
            pop_edit = st.number_input("Nova população", min_value=0, step=1)
            if st.form_submit_button("Atualizar município"):
                if not nome_edit.strip():
                    st.error("Informe um nome válido para atualizar o município.")
                else:
                    res = atualizar_municipio(int(id_alvo), nome_edit.strip(), int(uf_edit), int(pop_edit))
                    if res is None:
                        st.error("A API está fora do ar. Não foi possível atualizar o município.")
                    elif res.status_code == 200:
                        st.success("Município atualizado com sucesso!")
                    else:
                        st.error(f"Erro: {_extrair_erro(res)}")

        if st.button("Remover município", type="primary"):
            res = deletar_municipio(int(id_alvo))
            if res is None:
                st.error("A API está fora do ar. Não foi possível remover o município.")
            elif res.status_code == 200:
                st.success("Município e dados dependentes removidos!")
            else:
                st.error(f"Erro: {_extrair_erro(res)}")

with tab_gestor:
    st.markdown("### Anotações registradas")
    lista_acomp = listar_acompanhamentos()
    if lista_acomp:
        df_acomp = pd.DataFrame(lista_acomp)
        st.dataframe(df_acomp, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhuma anotação de gestor encontrada.")

    st.divider()
    col_criar_acomp, col_editar_acomp = st.columns(2)

    with col_criar_acomp:
        st.subheader("Cadastrar anotação")
        with st.form("form_criar_acomp"):
            id_mun_acomp = st.number_input("ID do município (existente)", min_value=1, step=1, key="add_mun")
            status_acomp = st.selectbox("Status", ["monitorando", "alerta", "resolvido"], key="add_status")
            prioridade_acomp = st.selectbox("Prioridade", ["baixa", "media", "alta"], key="add_prio")
            responsavel_acomp = st.text_input("Responsável", key="add_resp")
            obs_acomp = st.text_area("Observação", key="add_obs")
            if st.form_submit_button("Salvar anotação"):
                res = criar_acompanhamento(int(id_mun_acomp), status_acomp, prioridade_acomp, obs_acomp, responsavel_acomp)
                if res is None:
                    st.error("A API está fora do ar. Não foi possível salvar a anotação.")
                elif res.status_code == 201:
                    st.success("Anotação salva! Atualize a página para ver na tabela.")
                else:
                    st.error(f"Erro: {_extrair_erro(res)}")

    with col_editar_acomp:
        st.subheader("Atualizar ou remover anotação")
        id_alvo_acomp = st.number_input("ID da anotação (veja na tabela)", min_value=1, step=1, key="edit_id")
        with st.form("form_atualizar_acomp"):
            status_edit = st.selectbox("Status", ["monitorando", "alerta", "resolvido"], key="edit_status")
            prioridade_edit = st.selectbox("Prioridade", ["baixa", "media", "alta"], key="edit_prio")
            responsavel_edit = st.text_input("Responsável", key="edit_resp")
            obs_edit = st.text_area("Observação", key="edit_obs")
            if st.form_submit_button("Atualizar anotação"):
                res = atualizar_acompanhamento(int(id_alvo_acomp), status_edit, prioridade_edit, obs_edit, responsavel_edit)
                if res is None:
                    st.error("A API está fora do ar. Não foi possível atualizar a anotação.")
                elif res.status_code == 200:
                    st.success("Anotação atualizada! Atualize a página.")
                else:
                    st.error(f"Erro: {_extrair_erro(res)}")

        if st.button("Remover anotação", type="primary", key="del_acomp"):
            res = deletar_acompanhamento(int(id_alvo_acomp))
            if res is None:
                st.error("A API está fora do ar. Não foi possível remover a anotação.")
            elif res.status_code == 200:
                st.success("Anotação removida! Atualize a página.")
            else:
                st.error(f"Erro: {_extrair_erro(res)}")