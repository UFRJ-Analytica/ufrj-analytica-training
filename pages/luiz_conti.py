import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px

API_URL = "http://127.0.0.1:8000/luiz-conti"


def get(endpoint, params=None):
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        st.error("Erro de conexão com a API.")
        return None


st.title("Acompanhamento Populacional")

kpis = get("/estatisticas/resumo")
if kpis:
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1.3])
    col1.metric("Municípios", kpis["total_municipios"])
    col2.metric("Estados", kpis["total_estados"])
    col3.metric("População total", f"{kpis['populacao_total']:,}".replace(",", "."))
    col4.metric("Mais populoso", kpis["municipio_mais_populoso"])
    st.caption(f"Ano de referência: {kpis['ano_referencia']}")

st.divider()

st.subheader("Ranking municípios mais populosos")
limite = st.number_input("Quantidade", min_value=1, max_value=100, value=10, step=1)
ranking = get("/populacao/top-municipios", params={"limit": int(limite)})
if ranking:
    df_ranking = pd.DataFrame(ranking)
    st.dataframe(df_ranking, width="stretch", hide_index=True)
    st.plotly_chart(px.bar(df_ranking, x="nome_municipio", y="populacao"))

st.divider()

st.subheader("População por região")
regioes = get("/populacao/por-regiao")
if regioes:
    df_regioes = pd.DataFrame(regioes)
    st.plotly_chart(px.pie(df_regioes, names="nome_regiao", values="populacao"))

st.divider()

st.subheader("População por estado")

lista_regioes = get("/regioes")
nomes_regioes = {r["nome_regiao"]: r["id_regiao"] for r in lista_regioes} if lista_regioes else {}
regiao_selecionada = st.selectbox("Filtrar por região", ["Todas"] + list(nomes_regioes.keys()))

params_uf = None
if regiao_selecionada != "Todas":
    params_uf = {"id_regiao": nomes_regioes[regiao_selecionada]}

por_uf = get("/populacao/por-uf", params=params_uf)
if por_uf:
    df_uf = pd.DataFrame(por_uf)
    st.plotly_chart(px.bar(df_uf, x="sigla_uf", y="populacao"))

st.divider()

st.subheader("Distribuição da população dos municípios")
distribuicao = get("/populacao/distribuicao")
if distribuicao:
    df_dist = pd.DataFrame(distribuicao)
    fig_dist = px.histogram(df_dist, x="populacao", nbins=50)
    st.plotly_chart(fig_dist)

st.divider()

st.subheader("Municípios x população média por estado")
dispersao = get("/populacao/dispersao-uf")
if dispersao:
    df_disp = pd.DataFrame(dispersao)
    st.plotly_chart(
        px.scatter(df_disp, x="quantidade_municipios", y="populacao_media",
                   color="nome_regiao", hover_name="sigla_uf", log_y=True)
    )

st.divider()

st.subheader("Mapa de calor: região x porte")
heatmap = get("/populacao/heatmap-regiao-porte")
if heatmap:
    df_heat = pd.DataFrame(heatmap)

    ordem_porte = ["Pequeno", "Médio", "Grande"]

    pivot = df_heat.pivot_table(
        index="nome_regiao",
        columns="porte",
        values="quantidade_municipios",
        fill_value=0,
    )

    for porte in ordem_porte:
        if porte not in pivot.columns:
            pivot[porte] = 0
    pivot = pivot[ordem_porte]

    st.plotly_chart(
        px.imshow(
            pivot,
            text_auto=True,
            labels=dict(x="Porte", y="Região", color="Municípios"),
            aspect="auto",
            color_continuous_scale="Blues",
        )
    )
else:
    st.warning("Nenhum dado retornado pelo endpoint de heatmap.")

st.divider()

st.header("Cadastro")

tab1, tab2 = st.tabs(["Município (dados básicos)", "Anotações do gestor"])

with tab1:
    st.subheader("Criar novo município")
    with st.form("form_criar_municipio"):
        nome = st.text_input("Nome do município")
        id_uf = st.number_input("ID do estado (id_uf)", step=1)
        populacao = st.number_input("População", step=1)
        ano = st.number_input("Ano de referência", value=2025, step=1)
        fonte = st.text_input("Fonte")
        if st.form_submit_button("Criar"):
            resposta = requests.post(f"{API_URL}/municipios", json={
                "nome_municipio": nome, "id_uf": int(id_uf),
                "populacao": int(populacao), "ano": int(ano),
                "fonte": fonte
            })
            if resposta.ok:
                st.success("Município criado!")
            else:
                st.error(resposta.text)

    st.subheader("Editar / remover município existente")
    id_editar = st.number_input("ID do município", step=1, key="id_editar")
    col1, col2 = st.columns(2)

    with col1:
        with st.form("form_editar_municipio"):
            novo_nome = st.text_input("Novo nome (opcional)")
            novo_uf = st.number_input("Novo id_uf (opcional)", step=1, value=0)
            nova_pop = st.number_input("Nova população (opcional)", step=1, value=0)
            nova_fonte = st.text_input("Nova fonte (opcional)")
            if st.form_submit_button("Atualizar"):
                payload = {}
                if novo_nome:
                    payload["nome_municipio"] = novo_nome
                if novo_uf:
                    payload["id_uf"] = int(novo_uf)
                if nova_pop:
                    payload["populacao"] = int(nova_pop)
                if nova_fonte:
                    payload["fonte"] = nova_fonte
                resposta = requests.put(f"{API_URL}/municipios/{int(id_editar)}", json=payload)
                if resposta.ok:
                    st.success("Município atualizado!")
                else:
                    st.error(resposta.text)

    with col2:
        if st.button("Remover município"):
            resposta = requests.delete(f"{API_URL}/municipios/{int(id_editar)}")
            if resposta.ok:
                st.success("Município removido!")
            else:
                st.error(resposta.text)

with tab2:
    st.subheader("Nova anotação")
    with st.form("form_criar_cadastro"):
        id_municipio = st.number_input("ID do município", step=1)
        status = st.text_input("Status")
        prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
        observacao = st.text_area("Observação")
        responsavel = st.text_input("Responsável")
        if st.form_submit_button("Salvar"):
            resposta = requests.post(f"{API_URL}/cadastro", json={
                "id_municipio": int(id_municipio), "status": status,
                "prioridade": prioridade, "observacao": observacao,
                "responsavel": responsavel
            })
            if resposta.ok:
                st.success("Anotação criada!")
            else:
                st.error(resposta.text)

    st.subheader("Anotações existentes")
    filtro_id = st.number_input("Filtrar por ID do município (0 = todos)", step=1, value=0)
    params = {"id_municipio": filtro_id} if filtro_id else None
    cadastros = get("/cadastro", params=params)

    if cadastros:
        for c in cadastros:
            with st.expander(f"#{c['id_cadastro']} — Município {c['id_municipio']} — {c['status']}"):
                st.write(f"**Prioridade:** {c['prioridade']}")
                st.write(f"**Observação:** {c['observacao']}")
                st.write(f"**Responsável:** {c['responsavel']}")

    st.subheader("Editar / remover anotação existente")
    id_cadastro_editar = st.number_input("ID da anotação", step=1, key="id_cadastro_editar")
    col1, col2 = st.columns(2)

    with col1:
        with st.form("form_editar_cadastro"):
            novo_status = st.text_input("Novo status (opcional)")
            nova_prioridade = st.selectbox("Nova prioridade (opcional)", ["Baixa", "Média", "Alta"])
            nova_observacao = st.text_area("Nova observação (opcional)")
            novo_responsavel = st.text_input("Novo responsável (opcional)")
            if st.form_submit_button("Atualizar"):
                payload = {}
                if novo_status:
                    payload["status"] = novo_status
                if nova_prioridade:
                    payload["prioridade"] = nova_prioridade
                if nova_observacao:
                    payload["observacao"] = nova_observacao
                if novo_responsavel:
                    payload["responsavel"] = novo_responsavel
                resposta = requests.put(f"{API_URL}/cadastro/{int(id_cadastro_editar)}", json=payload)
                if resposta.ok:
                    st.success("Anotação atualizada!")
                else:
                    st.error(resposta.text)

    with col2:
        if st.button("Remover anotação"):
            resposta = requests.delete(f"{API_URL}/cadastro/{int(id_cadastro_editar)}")
            if resposta.ok:
                st.success("Anotação removida!")
            else:
                st.error(resposta.text)