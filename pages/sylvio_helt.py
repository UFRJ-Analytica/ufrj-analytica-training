import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000/sylvio-helt"

st.title("Entrega WebDev — Sylvio Helt")


st.header("KPIs")

try:
    kpis = requests.get(f"{API_URL}/kpis").json()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Municípios", kpis["total_municipios"])
    col2.metric("Estados", kpis["total_estados"])
    col3.metric("População total", f"{kpis['populacao_total']:,}".replace(",", "."))
    col4.metric("Ano de referência", kpis["ano_referencia"])
    col5.metric("Mais populoso", kpis["municipio_mais_populoso"])
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar os KPIs.")

st.divider()


st.header("Análise")


st.subheader("Top municípios mais populosos")

n = st.slider("Quantidade", min_value=5, max_value=50, value=10, step=5)

try:
    top_municipios = requests.get(f"{API_URL}/top-municipios", params={"n": n}).json()
    df_top = pd.DataFrame(top_municipios)

    st.dataframe(df_top, use_container_width=True)

    fig_top = px.bar(
        df_top,
        x="nome_municipio",
        y="populacao",
        color="sigla_uf",
        title=f"Top {n} municípios mais populosos",
    )
    st.plotly_chart(fig_top, use_container_width=True)
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar o top de municípios.")


st.subheader("População por região")

try:
    pop_regiao = requests.get(f"{API_URL}/populacao-por-regiao").json()
    df_regiao = pd.DataFrame(pop_regiao)

    fig_regiao = px.pie(
        df_regiao,
        names="nome_regiao",
        values="populacao_total",
        title="Distribuição da população por região",
    )
    st.plotly_chart(fig_regiao, use_container_width=True)
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar a população por região.")


st.subheader("População por estado")

try:
    regioes_disponiveis = {r["nome_regiao"]: r["id_regiao"] for r in pop_regiao}
    opcoes_regiao = ["Todas"] + list(regioes_disponiveis.keys())
    regiao_selecionada = st.selectbox("Filtrar por região", opcoes_regiao)

    params = {}
    if regiao_selecionada != "Todas":
        params["id_regiao"] = regioes_disponiveis[regiao_selecionada]

    pop_estado = requests.get(f"{API_URL}/populacao-por-estado", params=params).json()
    df_estado = pd.DataFrame(pop_estado)

    fig_estado = px.bar(
        df_estado,
        x="sigla_uf",
        y="populacao_total",
        title="População total por estado",
    )
    st.plotly_chart(fig_estado, use_container_width=True)
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar a população por estado.")


st.subheader("Distribuição da população dos municípios")

try:
    distribuicao = requests.get(f"{API_URL}/distribuicao-populacao").json()
    df_dist = pd.DataFrame(distribuicao)

    fig_dist = px.histogram(
        df_dist,
        x="populacao",
        nbins=50,
        title="Distribuição da população entre os municípios",
    )
    st.plotly_chart(fig_dist, use_container_width=True)
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar a distribuição de população.")


st.subheader("Dispersão: municípios x população média por estado")

try:
    dispersao = requests.get(f"{API_URL}/dispersao-estados").json()
    df_disp = pd.DataFrame(dispersao)

    fig_disp = px.scatter(
        df_disp,
        x="qtd_municipios",
        y="populacao_media",
        color="nome_regiao",
        hover_name="sigla_uf",
        title="Quantidade de municípios x população média, por estado",
    )
    st.plotly_chart(fig_disp, use_container_width=True)
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar os dados de dispersão.")


st.subheader("Mapa de calor: região x porte do município")

try:
    heatmap_data = requests.get(f"{API_URL}/heatmap-regiao-porte").json()
    df_heat = pd.DataFrame(heatmap_data)

    tabela_heat = df_heat.pivot(index="nome_regiao", columns="porte", values="qtd_municipios").fillna(0)

    fig_heat = px.imshow(
        tabela_heat,
        text_auto=True,
        labels=dict(x="Porte", y="Região", color="Qtd. municípios"),
        title="Quantidade de municípios por região e porte",
    )
    st.plotly_chart(fig_heat, use_container_width=True)
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar o mapa de calor.")

st.divider()



st.header("Cadastro")


st.subheader("Município (dados básicos)")

try:
    estados_disponiveis = {f"{e['sigla_uf']} - {e['nome_uf']}": e["id_uf"] for e in pop_estado}
except NameError:
    # caso a chamada de população por estado acima tenha falhado
    todos_estados = requests.get(f"{API_URL}/populacao-por-estado").json()
    estados_disponiveis = {f"{e['sigla_uf']} - {e['nome_uf']}": e["id_uf"] for e in todos_estados}

aba_criar, aba_atualizar, aba_remover = st.tabs(["Criar novo", "Atualizar existente", "Remover"])

with aba_criar:
    with st.form("form_criar_municipio"):
        nome_novo = st.text_input("Nome do município")
        estado_novo = st.selectbox("Estado", list(estados_disponiveis.keys()), key="estado_novo")
        populacao_nova = st.number_input("População", min_value=0, step=1)
        enviar_criar = st.form_submit_button("Criar município")

    if enviar_criar:
        payload = {
            "nome_municipio": nome_novo,
            "id_uf": estados_disponiveis[estado_novo],
            "populacao": int(populacao_nova),
        }
        try:
            r = requests.post(f"{API_URL}/municipios", json=payload)
            r.raise_for_status()
            st.success(f"Município criado com id {r.json()['id_municipio']}.")
        except requests.exceptions.RequestException:
            st.error("Não foi possível criar o município.")

with aba_atualizar:
    id_atualizar = st.number_input("ID do município", min_value=1, step=1, key="id_atualizar")

    if st.button("Buscar município"):
        try:
            r = requests.get(f"{API_URL}/municipios/{int(id_atualizar)}")
            r.raise_for_status()
            st.session_state["municipio_encontrado"] = r.json()
        except requests.exceptions.RequestException:
            st.error("Município não encontrado.")
            st.session_state["municipio_encontrado"] = None

    if st.session_state.get("municipio_encontrado"):
        municipio = st.session_state["municipio_encontrado"]

        with st.form("form_atualizar_municipio"):
            nome_att = st.text_input("Nome do município", value=municipio["nome_municipio"])
            populacao_att = st.number_input(
                "População", min_value=0, step=1, value=municipio["populacao"]
            )
            enviar_atualizar = st.form_submit_button("Salvar alterações")

        if enviar_atualizar:
            payload = {"nome_municipio": nome_att, "populacao": int(populacao_att)}
            try:
                r = requests.put(f"{API_URL}/municipios/{municipio['id_municipio']}", json=payload)
                r.raise_for_status()
                st.success("Município atualizado.")
            except requests.exceptions.RequestException:
                st.error("Não foi possível atualizar o município.")

with aba_remover:
    id_remover = st.number_input("ID do município", min_value=1, step=1, key="id_remover")

    if st.button("Remover município"):
        try:
            r = requests.delete(f"{API_URL}/municipios/{int(id_remover)}")
            r.raise_for_status()
            st.success("Município removido.")
        except requests.exceptions.RequestException:
            st.error("Não foi possível remover o município.")


st.subheader("Anotações do gestor")

id_municipio_cadastro = st.number_input(
    "ID do município para ver/gerenciar anotações", min_value=1, step=1, key="id_cadastro_municipio"
)

try:
    anotacoes = requests.get(
        f"{API_URL}/cadastro", params={"id_municipio": int(id_municipio_cadastro)}
    ).json()

    if anotacoes:
        st.dataframe(pd.DataFrame(anotacoes), use_container_width=True)
    else:
        st.info("Nenhuma anotação registrada para esse município ainda.")
except requests.exceptions.RequestException:
    st.error("Não foi possível carregar as anotações.")
    anotacoes = []

aba_nova, aba_editar, aba_apagar = st.tabs(["Nova anotação", "Editar", "Remover"])

with aba_nova:
    with st.form("form_nova_anotacao"):
        status_novo = st.text_input("Status")
        prioridade_nova = st.text_input("Prioridade")
        observacao_nova = st.text_area("Observação")
        responsavel_novo = st.text_input("Responsável")
        enviar_nova = st.form_submit_button("Criar anotação")

    if enviar_nova:
        payload = {
            "id_municipio": int(id_municipio_cadastro),
            "status": status_novo,
            "prioridade": prioridade_nova,
            "observacao": observacao_nova,
            "responsavel": responsavel_novo,
        }
        try:
            r = requests.post(f"{API_URL}/cadastro", json=payload)
            r.raise_for_status()
            st.success("Anotação criada.")
        except requests.exceptions.RequestException:
            st.error("Não foi possível criar a anotação.")

with aba_editar:
    id_cadastro_editar = st.number_input("ID da anotação", min_value=1, step=1, key="id_cadastro_editar")

    with st.form("form_editar_anotacao"):
        status_edit = st.text_input("Novo status (deixe em branco para não alterar)")
        prioridade_edit = st.text_input("Nova prioridade (deixe em branco para não alterar)")
        observacao_edit = st.text_area("Nova observação (deixe em branco para não alterar)")
        responsavel_edit = st.text_input("Novo responsável (deixe em branco para não alterar)")
        enviar_edicao = st.form_submit_button("Salvar edição")

    if enviar_edicao:
        payload = {}
        if status_edit:
            payload["status"] = status_edit
        if prioridade_edit:
            payload["prioridade"] = prioridade_edit
        if observacao_edit:
            payload["observacao"] = observacao_edit
        if responsavel_edit:
            payload["responsavel"] = responsavel_edit

        try:
            r = requests.put(f"{API_URL}/cadastro/{int(id_cadastro_editar)}", json=payload)
            r.raise_for_status()
            st.success("Anotação atualizada.")
        except requests.exceptions.RequestException:
            st.error("Não foi possível atualizar a anotação.")

with aba_apagar:
    id_cadastro_apagar = st.number_input("ID da anotação", min_value=1, step=1, key="id_cadastro_apagar")

    if st.button("Remover anotação"):
        try:
            r = requests.delete(f"{API_URL}/cadastro/{int(id_cadastro_apagar)}")
            r.raise_for_status()
            st.success("Anotação removida.")
        except requests.exceptions.RequestException:
            st.error("Não foi possível remover a anotação.")