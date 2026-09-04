"""
Tela de acompanhamento populacional — Isaac Vianna.

Consome só a API (backend/app/endpoints/isaac_vianna.py) via requests, nunca
acessa o database.db direto. Duas áreas: análise (gráficos) e cadastro
(CRUD de município + CRUD das anotações do gestor).
"""
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_ROOT = "http://127.0.0.1:8000"
API_BASE = f"{API_ROOT}/isaac-vianna"


def api_get(path: str, params: dict | None = None, base: str = API_BASE):
    try:
        resp = requests.get(f"{base}{path}", params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Não consegui falar com a API. Ela está rodando em http://127.0.0.1:8000?")
        return None
    except requests.exceptions.HTTPError:
        st.error(f"Erro da API: {resp.json().get('detail', resp.text)}")
        return None


def api_write(metodo: str, path: str, json: dict | None = None):
    try:
        resp = requests.request(metodo, f"{API_BASE}{path}", json=json, timeout=5)
        resp.raise_for_status()
        return resp.json() if resp.content else True
    except requests.exceptions.ConnectionError:
        st.error("Não consegui falar com a API. Ela está rodando em http://127.0.0.1:8000?")
        return None
    except requests.exceptions.HTTPError:
        st.error(f"Erro da API: {resp.json().get('detail', resp.text)}")
        return None


st.set_page_config(page_title="Acompanhamento Populacional", page_icon=":bar_chart:", layout="wide")
st.title("Acompanhamento Populacional (IBGE)")
st.caption("Isaac Vianna — API em /isaac-vianna")

# GET /regioes já é um endpoint global (sem o prefixo /isaac-vianna), reaproveitado como está.
regioes = api_get("/regioes", base=API_ROOT)

aba_analise, aba_cadastro = st.tabs(["Análise", "Cadastro"])

with aba_analise:
    resumo = api_get("/estatisticas/resumo")
    if resumo:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Municípios", resumo["total_municipios"])
        col2.metric("Estados", resumo["total_estados"])
        col3.metric("População total", f"{resumo['populacao_total']:,}".replace(",", "."))
        col4.metric("Ano de referência", resumo["ano_referencia"])
        col5.metric(
            "Mais populoso",
            f"{resumo['municipio_mais_populoso']}/{resumo['sigla_uf_mais_populoso']}",
            f"{resumo['populacao_mais_populoso']:,}".replace(",", "."),
        )

    st.divider()

    st.subheader("Top municípios mais populosos")
    n_top = st.slider("Quantidade", min_value=5, max_value=50, value=10, step=5)
    top_municipios = api_get("/populacao/top-municipios", params={"limit": n_top})
    if top_municipios:
        df_top = pd.DataFrame(top_municipios)
        col_tabela, col_grafico = st.columns(2)
        col_tabela.dataframe(df_top, hide_index=True, use_container_width=True)
        fig_top = px.bar(df_top, x="nome_municipio", y="populacao", color="sigla_uf")
        col_grafico.plotly_chart(fig_top, use_container_width=True)

    st.divider()

    col_pizza, col_barras = st.columns(2)

    with col_pizza:
        st.subheader("População por região")
        por_regiao = api_get("/populacao/por-regiao")
        if por_regiao:
            df_regiao = pd.DataFrame(por_regiao)
            fig_pizza = px.pie(df_regiao, names="nome_regiao", values="populacao_total", hole=0.4)
            st.plotly_chart(fig_pizza, use_container_width=True)

    with col_barras:
        st.subheader("População por estado")
        opcoes_regiao = {"Todas": None} | {r["nome_regiao"]: r["id_regiao"] for r in (regioes or [])}
        regiao_escolhida = st.selectbox("Filtrar por região", options=list(opcoes_regiao.keys()))
        id_regiao_filtro = opcoes_regiao[regiao_escolhida]
        params = {"id_regiao": id_regiao_filtro} if id_regiao_filtro else None
        por_uf = api_get("/populacao/por-uf", params=params)
        if por_uf:
            df_uf = pd.DataFrame(por_uf)
            fig_uf = px.bar(df_uf.sort_values("populacao_total", ascending=False), x="sigla_uf", y="populacao_total")
            st.plotly_chart(fig_uf, use_container_width=True)

    st.divider()

    col_hist, col_scatter = st.columns(2)

    with col_hist:
        st.subheader("Distribuição da população dos municípios")
        distribuicao = api_get("/populacao/distribuicao")
        if distribuicao:
            df_dist = pd.DataFrame(distribuicao)
            fig_hist = px.histogram(df_dist, x="populacao", nbins=50)
            st.plotly_chart(fig_hist, use_container_width=True)

    with col_scatter:
        st.subheader("Municípios x população média por estado")
        dispersao = api_get("/populacao/dispersao-uf")
        if dispersao:
            df_disp = pd.DataFrame(dispersao)
            fig_scatter = px.scatter(
                df_disp,
                x="quantidade_municipios",
                y="populacao_media",
                color="sigla_regiao",
                hover_name="nome_uf",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    st.subheader("Mapa de calor: região x porte do município")
    heatmap = api_get("/populacao/heatmap-regiao-porte")
    if heatmap:
        df_heat = pd.DataFrame(heatmap)
        tabela_heat = df_heat.pivot(index="sigla_regiao", columns="porte", values="quantidade")
        tabela_heat = tabela_heat[["pequeno", "medio", "grande"]]
        fig_heat = px.imshow(tabela_heat, text_auto=True, aspect="auto")
        st.plotly_chart(fig_heat, use_container_width=True)


with aba_cadastro:
    estados = api_get("/estados") or []
    mapa_estados = {f"{e['nome_uf']} ({e['sigla_uf']})": e["id_uf"] for e in estados}

    st.subheader("Município (dados básicos)")

    busca = st.text_input("Buscar município por nome")
    municipios = api_get("/municipios", params={"nome": busca, "limit": 20} if busca else {"limit": 20})
    opcoes_municipio = {"Novo município": None}
    if municipios:
        opcoes_municipio |= {
            f"{m['nome_municipio']} (id {m['id_municipio']})": m["id_municipio"] for m in municipios
        }

    municipio_escolhido = st.selectbox("Município", options=list(opcoes_municipio.keys()))
    id_municipio_selecionado = opcoes_municipio[municipio_escolhido]

    dados_municipio = None
    if id_municipio_selecionado is not None:
        dados_municipio = api_get(f"/municipios/{id_municipio_selecionado}")

    with st.form("form_municipio"):
        nome_input = st.text_input("Nome do município", value=dados_municipio["nome_municipio"] if dados_municipio else "")
        estado_default = 0
        if dados_municipio:
            uf_atual = next((e for e in estados if e["id_uf"] == dados_municipio["id_uf"]), None)
            if uf_atual:
                estado_default = list(mapa_estados.keys()).index(f"{uf_atual['nome_uf']} ({uf_atual['sigla_uf']})")
        estado_input = st.selectbox("Estado", options=list(mapa_estados.keys()), index=estado_default)
        populacao_input = st.number_input(
            "População", min_value=0, step=1, value=dados_municipio["populacao"] if dados_municipio else 0
        )

        col_salvar, col_remover = st.columns(2)
        salvar = col_salvar.form_submit_button("Salvar")
        remover = col_remover.form_submit_button("Remover", disabled=id_municipio_selecionado is None)

        if salvar:
            payload = {
                "nome_municipio": nome_input,
                "id_uf": mapa_estados[estado_input],
                "populacao": int(populacao_input),
            }
            if id_municipio_selecionado is None:
                resultado = api_write("POST", "/municipios", json=payload)
            else:
                resultado = api_write("PUT", f"/municipios/{id_municipio_selecionado}", json=payload)
            if resultado:
                st.success("Município salvo.")
                st.rerun()

        if remover and id_municipio_selecionado is not None:
            resultado = api_write("DELETE", f"/municipios/{id_municipio_selecionado}")
            if resultado is not None:
                st.success("Município removido.")
                st.rerun()

    st.divider()
    st.subheader("Cadastro (anotação do gestor)")

    if id_municipio_selecionado is None:
        st.info("Escolha um município já existente para ver/gerenciar as anotações do gestor.")
    else:
        registros = api_get(f"/municipios/{id_municipio_selecionado}/registros") or []

        if registros:
            for registro in registros:
                with st.expander(
                    f"[{registro['prioridade']}] {registro['status']} — atualizado em {registro['atualizado_em']}"
                ):
                    with st.form(f"editar_registro_{registro['id_registro']}"):
                        status_edit = st.text_input("Status", value=registro["status"])
                        prioridade_edit = st.selectbox(
                            "Prioridade",
                            options=["baixa", "media", "alta"],
                            index=["baixa", "media", "alta"].index(registro["prioridade"]),
                        )
                        observacao_edit = st.text_area("Observação", value=registro["observacao"] or "")
                        responsavel_edit = st.text_input("Responsável", value=registro["responsavel"] or "")

                        col_editar, col_apagar = st.columns(2)
                        editar = col_editar.form_submit_button("Salvar edição")
                        apagar = col_apagar.form_submit_button("Remover registro")

                        if editar:
                            resultado = api_write(
                                "PUT",
                                f"/registros/{registro['id_registro']}",
                                json={
                                    "status": status_edit,
                                    "prioridade": prioridade_edit,
                                    "observacao": observacao_edit,
                                    "responsavel": responsavel_edit,
                                },
                            )
                            if resultado:
                                st.success("Registro atualizado.")
                                st.rerun()

                        if apagar:
                            resultado = api_write("DELETE", f"/registros/{registro['id_registro']}")
                            if resultado is not None:
                                st.success("Registro removido.")
                                st.rerun()
        else:
            st.caption("Nenhuma anotação registrada para este município ainda.")

        st.markdown("**Novo registro**")
        with st.form("novo_registro"):
            status_novo = st.text_input("Status", value="normal")
            prioridade_novo = st.selectbox("Prioridade", options=["baixa", "media", "alta"])
            observacao_novo = st.text_area("Observação")
            responsavel_novo = st.text_input("Responsável")
            criar = st.form_submit_button("Criar registro")

            if criar:
                resultado = api_write(
                    "POST",
                    f"/municipios/{id_municipio_selecionado}/registros",
                    json={
                        "status": status_novo,
                        "prioridade": prioridade_novo,
                        "observacao": observacao_novo,
                        "responsavel": responsavel_novo,
                    },
                )
                if resultado:
                    st.success("Registro criado.")
                    st.rerun()
