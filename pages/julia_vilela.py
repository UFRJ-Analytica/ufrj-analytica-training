

import requests
import pandas as pd
import streamlit as st
import plotly.express as px


API_BASE = "http://127.0.0.1:8000"
PREFIX = "/julia-vilela"          
API = f"{API_BASE}{PREFIX}"

st.set_page_config(page_title="Acompanhamento Populacional", layout="wide")


# ---------------------------------------------------------------------------
# Helper de requisição: trata API fora do ar sem quebrar a tela
# ---------------------------------------------------------------------------
def api_get(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Não foi possível conectar na API. Ela está rodando? (uvicorn ...)")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Erro da API ({r.status_code}): {r.text}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None


def api_send(method: str, path: str, json: dict | None = None):
    try:
        r = requests.request(method, f"{API}{path}", json=json, timeout=10)
        if r.status_code >= 400:
            st.error(f"Erro da API ({r.status_code}): {r.text}")
            return None
        return r.json() if r.text else {}
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Não foi possível conectar na API.")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None


st.title("📊 Acompanhamento Populacional dos Municípios")

aba_analise, aba_municipio, aba_cadastro = st.tabs(
    ["📈 Análise", "🏙️ Municípios", "📝 Cadastro do gestor"]
)


# ###########################################################################
#  ABA 1 — ANÁLISE
# ###########################################################################
with aba_analise:
    # ---- KPIs -------------------------------------------------------------
    kpis = api_get("/kpis")
    if kpis:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Municípios", f"{kpis['total_municipios']:,}".replace(",", "."))
        c2.metric("Estados", kpis["total_estados"])
        c3.metric("População total", f"{kpis['populacao_total']:,}".replace(",", "."))
        c4.metric("Ano de referência", kpis["ano_referencia"])
        mp = kpis.get("municipio_mais_populoso")
        if mp:
            st.caption(
                f"🏆 Mais populoso: **{mp['municipio']} ({mp['uf']})** — "
                f"{mp['populacao']:,}".replace(",", ".") + " hab."
            )

    st.divider()

    # ---- Top N municípios -------------------------------------------------
    col_a, col_b = st.columns([1, 3])
    with col_a:
        n = st.slider("Top N municípios", 3, 30, 10)
    top = api_get("/top-municipios", {"n": n})
    if top:
        df_top = pd.DataFrame(top)
        col_esq, col_dir = st.columns(2)
        with col_esq:
            st.subheader("Tabela")
            st.dataframe(df_top, use_container_width=True, hide_index=True)
        with col_dir:
            st.subheader("Gráfico de barras")
            fig = px.bar(
                df_top.sort_values("populacao"),
                x="populacao", y="municipio", orientation="h",
                labels={"populacao": "População", "municipio": "Município"},
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Pizza por região + barras por estado -----------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("População por região")
        reg = api_get("/populacao-por-regiao")
        if reg:
            df_reg = pd.DataFrame(reg)
            fig = px.pie(df_reg, names="regiao", values="populacao", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("População por estado")
        regioes_opts = ["(todas)"] + (
            [r["regiao"] for r in reg] if reg else []
        )
        filtro_regiao = st.selectbox("Filtrar por região", regioes_opts)
        params = None if filtro_regiao == "(todas)" else {"regiao": filtro_regiao}
        est = api_get("/populacao-por-estado", params)
        if est:
            df_est = pd.DataFrame(est)
            fig = px.bar(
                df_est.sort_values("populacao"),
                x="populacao", y="uf", orientation="h", color="regiao",
                labels={"populacao": "População", "uf": "UF"},
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Histograma de distribuição ---------------------------------------
    st.subheader("Distribuição da população dos municípios")
    dist = api_get("/distribuicao-populacao")
    if dist:
        df_dist = pd.DataFrame({"populacao": dist})
        usar_log = st.checkbox("Escala logarítmica no eixo X (recomendado)", value=True)
        fig = px.histogram(df_dist, x="populacao", nbins=60, log_x=usar_log)
        fig.update_layout(yaxis_title="Nº de municípios", xaxis_title="População")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Dispersão --------------------------------------------------------
    st.subheader("Dispersão: nº de municípios × população média por estado")
    disp = api_get("/dispersao-estados")
    if disp:
        df_disp = pd.DataFrame(disp)
        fig = px.scatter(
            df_disp, x="qtd_municipios", y="populacao_media",
            color="regiao", hover_name="estado", size="qtd_municipios",
            labels={"qtd_municipios": "Qtd de municípios", "populacao_media": "População média"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- Heatmap região x porte -------------------------------------------
    st.subheader("Mapa de calor: região × porte do município")
    heat = api_get("/heatmap-regiao-porte")
    if heat:
        df_heat = pd.DataFrame(heat)
        ordem_porte = ["pequeno", "medio", "grande"]
        matriz = (
            df_heat.pivot_table(index="regiao", columns="porte", values="quantidade", fill_value=0)
            .reindex(columns=ordem_porte, fill_value=0)
        )
        fig = px.imshow(
            matriz, text_auto=True, aspect="auto",
            color_continuous_scale="Blues",
            labels={"x": "Porte", "y": "Região", "color": "Nº municípios"},
        )
        st.plotly_chart(fig, use_container_width=True)


# ###########################################################################
#  ABA 2 — MUNICÍPIOS (dados básicos: criar / editar / remover)
# ###########################################################################
with aba_municipio:
    st.subheader("Buscar municípios")
    busca = st.text_input("Nome do município (parcial)")
    resultados = api_get("/municipios", {"q": busca} if busca else None)
    if resultados:
        st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)

    st.divider()
    col_novo, col_edit = st.columns(2)

    # ---- Criar ------------------------------------------------------------
    with col_novo:
        st.subheader("➕ Novo município")
        with st.form("form_novo_mun"):
            nome = st.text_input("Nome")
            uf = st.text_input("UF (ex.: RJ)").upper()
            pop = st.number_input("População", min_value=0, step=1)
            if st.form_submit_button("Criar"):
                res = api_send("POST", "/municipios",
                               {"nome": nome, "uf": uf, "populacao": int(pop)})
                if res:
                    st.success(f"Criado! id_municipio = {res['id_municipio']}")

    # ---- Editar / Remover -------------------------------------------------
    with col_edit:
        st.subheader("✏️ Editar / 🗑️ Remover")
        id_mun = st.number_input("id_municipio", min_value=1, step=1, key="edit_mun_id")
        if st.button("Carregar dados"):
            dado = api_get(f"/municipios/{int(id_mun)}")
            if dado:
                st.session_state["mun_edit"] = dado
        dado = st.session_state.get("mun_edit")
        if dado:
            with st.form("form_edit_mun"):
                novo_nome = st.text_input("Nome", value=dado["municipio"])
                nova_uf = st.text_input("UF", value=dado["uf"]).upper()
                nova_pop = st.number_input("População", min_value=0, step=1,
                                           value=int(dado["populacao"]))
                col_s, col_d = st.columns(2)
                if col_s.form_submit_button("Salvar"):
                    res = api_send("PUT", f"/municipios/{dado['id_municipio']}",
                                   {"nome": novo_nome, "uf": nova_uf, "populacao": int(nova_pop)})
                    if res:
                        st.success("Atualizado!")
                        st.session_state["mun_edit"] = res
                if col_d.form_submit_button("Remover"):
                    r = requests.delete(f"{API}/municipios/{dado['id_municipio']}")
                    if r.status_code == 204:
                        st.success("Removido!")
                        st.session_state.pop("mun_edit", None)
                    else:
                        st.error(f"Erro: {r.text}")


# ###########################################################################
#  ABA 3 — CADASTRO DO GESTOR (anotações)
# ###########################################################################
with aba_cadastro:
    st.subheader("Anotações de acompanhamento")

    # ---- Listar -----------------------------------------------------------
    filtro_id = st.number_input("Filtrar por id_municipio (0 = todos)",
                                min_value=0, step=1, value=0)
    params = {"id_municipio": int(filtro_id)} if filtro_id else None
    lista = api_get("/acompanhamentos", params)
    if lista is not None:
        if lista:
            st.dataframe(pd.DataFrame(lista), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma anotação ainda.")

    st.divider()
    col_c, col_e = st.columns(2)

    STATUS_OPTS = ["monitorando", "prioridade", "arquivado"]
    PRIOR_OPTS = ["baixa", "media", "alta"]

    # ---- Criar ------------------------------------------------------------
    with col_c:
        st.subheader("➕ Nova anotação")
        with st.form("form_novo_acomp"):
            id_m = st.number_input("id_municipio", min_value=1, step=1)
            status = st.selectbox("Status", STATUS_OPTS)
            prioridade = st.selectbox("Prioridade", PRIOR_OPTS, index=1)
            responsavel = st.text_input("Responsável")
            observacao = st.text_area("Observação")
            if st.form_submit_button("Criar"):
                res = api_send("POST", "/acompanhamentos", {
                    "id_municipio": int(id_m), "status": status,
                    "prioridade": prioridade, "observacao": observacao,
                    "responsavel": responsavel,
                })
                if res:
                    st.success(f"Anotação criada (id {res['id']})")

    # ---- Editar / Remover -------------------------------------------------
    with col_e:
        st.subheader("✏️ Editar / 🗑️ Remover")
        id_a = st.number_input("id da anotação", min_value=1, step=1, key="acomp_id")
        if st.button("Carregar anotação"):
            todas = api_get("/acompanhamentos") or []
            achou = next((a for a in todas if a["id"] == int(id_a)), None)
            st.session_state["acomp_edit"] = achou
            if not achou:
                st.warning("Anotação não encontrada.")
        acomp = st.session_state.get("acomp_edit")
        if acomp:
            with st.form("form_edit_acomp"):
                status = st.selectbox("Status", STATUS_OPTS,
                                      index=STATUS_OPTS.index(acomp["status"])
                                      if acomp["status"] in STATUS_OPTS else 0)
                prioridade = st.selectbox("Prioridade", PRIOR_OPTS,
                                          index=PRIOR_OPTS.index(acomp["prioridade"])
                                          if acomp["prioridade"] in PRIOR_OPTS else 1)
                responsavel = st.text_input("Responsável", value=acomp.get("responsavel") or "")
                observacao = st.text_area("Observação", value=acomp.get("observacao") or "")
                col_s, col_d = st.columns(2)
                if col_s.form_submit_button("Salvar"):
                    res = api_send("PUT", f"/acompanhamentos/{acomp['id']}", {
                        "status": status, "prioridade": prioridade,
                        "observacao": observacao, "responsavel": responsavel,
                    })
                    if res:
                        st.success("Atualizado!")
                        st.session_state["acomp_edit"] = res
                if col_d.form_submit_button("Remover"):
                    r = requests.delete(f"{API}/acompanhamentos/{acomp['id']}")
                    if r.status_code == 204:
                        st.success("Removido!")
                        st.session_state.pop("acomp_edit", None)
                    else:
                        st.error(f"Erro: {r.text}")