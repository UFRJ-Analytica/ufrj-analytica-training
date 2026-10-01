import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Acompanhamento Populacional", layout="wide")
st.title("Acompanhamento Populacional dos Municípios")


# helpers de chamada a API, com tratamento de erro de conexao
def get(endpoint, params=None):
    try:
        resp = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.exception(e)
        return None


def post(endpoint, json=None):
    try:
        resp = requests.post(f"{API_URL}{endpoint}", json=json, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao criar: {e}")
        return None


def put(endpoint, json=None):
    try:
        resp = requests.put(f"{API_URL}{endpoint}", json=json, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao atualizar: {e}")
        return None


def delete(endpoint):
    try:
        resp = requests.delete(f"{API_URL}{endpoint}", timeout=5)
        resp.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao remover: {e}")
        return False


tab_analise, tab_cadastro = st.tabs(["📊 Análise", "📝 Cadastro"])

# --- aba de analise ---
with tab_analise:
    kpis = get("/estatisticas/resumo")
    if kpis:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Municípios", f"{kpis['total_municipios']:,}".replace(",", "."))
        c2.metric("Estados", kpis["total_estados"])
        c3.metric("População total", f"{kpis['populacao_total']:,.0f}".replace(",", "."))
        c4.metric("Ano de referência", kpis["ano_referencia"])
        st.caption(
            f"Mais populoso: **{kpis['municipio_mais_populoso']}** "
            f"({kpis['populacao_municipio_mais_populoso']:,.0f} hab.)".replace(",", ".")
        )

    st.divider()
    st.subheader("Top municípios mais populosos")
    n = st.slider("Quantidade", 5, 50, 10, step=5)
    top = get("/populacao/top-municipios", params={"limit": n})
    if top:
        df_top = pd.DataFrame(top)
        col_a, col_b = st.columns(2)
        col_a.dataframe(df_top, hide_index=True, use_container_width=True)
        col_b.plotly_chart(px.bar(df_top, x="nome_municipio", y="populacao"), use_container_width=True)

    st.divider()
    st.subheader("População por região")
    por_regiao = get("/populacao/por-regiao")
    if por_regiao:
        df_r = pd.DataFrame(por_regiao)
        st.plotly_chart(px.pie(df_r, names="nome_regiao", values="populacao", hole=0.4), use_container_width=True)

    st.divider()
    st.subheader("População por estado")
    regioes = get("/regioes") or []
    opcoes_regiao = {"Todas": None} | {r["nome_regiao"]: r["id_regiao"] for r in regioes}
    regiao_sel = st.selectbox("Filtrar por região", list(opcoes_regiao.keys()))
    params = {"id_regiao": opcoes_regiao[regiao_sel]} if opcoes_regiao[regiao_sel] else None
    por_estado = get("/populacao/por-uf", params=params)
    if por_estado:
        df_e = pd.DataFrame(por_estado)
        st.plotly_chart(px.bar(df_e, x="sigla_uf", y="populacao"), use_container_width=True)

    st.divider()
    st.subheader("Distribuição da população")
    dist = get("/populacao/distribuicao")
    if dist:
        df_d = pd.DataFrame(dist)
        st.plotly_chart(px.histogram(df_d, x="populacao", nbins=50), use_container_width=True)

    st.divider()
    st.subheader("Municípios x população média por estado")
    disp = get("/populacao/dispersao-uf")
    if disp:
        df_disp = pd.DataFrame(disp)
        fig = px.scatter(df_disp, x="qtd_municipios", y="populacao_media", color="nome_regiao", hover_name="nome_uf")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Mapa de calor: região x porte")
    heat = get("/populacao/heatmap-regiao-porte")
    if heat:
        df_h = pd.DataFrame(heat)
        pivot = df_h.pivot(index="regiao", columns="porte", values="quantidade").fillna(0)
        st.plotly_chart(px.imshow(pivot, text_auto=True, aspect="auto"), use_container_width=True)


# --- aba de cadastro ---
with tab_cadastro:
    st.subheader("Município")
    modo = st.radio("Ação", ["Criar novo município", "Editar município existente"])

    if modo == "Criar novo município":
        with st.form("form_criar_municipio"):
            nome = st.text_input("Nome do município")
            estados_lista = get("/estados") or []
            opcoes_uf = {e["nome_uf"]: e["id_uf"] for e in estados_lista}
            uf_nome = st.selectbox("Estado", list(opcoes_uf.keys()))
            populacao_input = st.number_input("População", min_value=0, step=1)
            if st.form_submit_button("Criar município"):
                resultado = post("/municipios", json={
                    "nome_municipio": nome,
                    "id_uf": opcoes_uf[uf_nome],
                    "populacao": int(populacao_input),
                })
                if resultado:
                    st.success(f"Criado com id {resultado['id_municipio']}.")
                    st.rerun()
    else:
        id_edicao = st.number_input("ID do município", min_value=1, step=1)
        if st.button("Buscar"):
            municipio = get(f"/municipios/{int(id_edicao)}")
            if municipio:
                st.session_state["municipio_edicao"] = municipio

        # guarda o municipio buscado no session_state pra sobreviver ao rerun do form
        m = st.session_state.get("municipio_edicao")
        if m:
            with st.form("form_editar_municipio"):
                novo_nome = st.text_input("Nome", value=m["nome_municipio"])
                nova_pop = st.number_input("População", min_value=0, step=1, value=int(m["populacao"] or 0))
                if st.form_submit_button("Salvar alterações"):
                    resultado = put(f"/municipios/{m['id_municipio']}", json={
                        "nome_municipio": novo_nome,
                        "populacao": int(nova_pop),
                    })
                    if resultado:
                        st.success("Atualizado.")
                        st.rerun()

            if st.button("Remover este município", type="primary"):
                if delete(f"/municipios/{m['id_municipio']}"):
                    st.success("Removido.")
                    del st.session_state["municipio_edicao"]
                    st.rerun()

    st.divider()
    st.subheader("Registros de acompanhamento do gestor")
    id_mun_reg = st.number_input("ID do município", min_value=1, step=1, key="id_municipio_registros")

    with st.expander("Adicionar novo registro"):
        with st.form("form_criar_registro"):
            status = st.text_input("Status", value="monitorando")
            prioridade = st.selectbox("Prioridade", ["baixa", "media", "alta"])
            observacao = st.text_area("Observação")
            responsavel = st.text_input("Responsável")
            if st.form_submit_button("Adicionar registro"):
                resultado = post(f"/municipios/{int(id_mun_reg)}/registros", json={
                    "status": status,
                    "prioridade": prioridade,
                    "observacao": observacao,
                    "responsavel": responsavel,
                })
                if resultado:
                    st.success("Registro criado.")
                    st.rerun()

    # cada registro vira um card, com edicao inline via popover
    registros = get(f"/municipios/{int(id_mun_reg)}/registros")
    if registros:
        for reg in registros:
            with st.container(border=True):
                st.write(f"**Status:** {reg['status']} | **Prioridade:** {reg['prioridade']}")
                st.write(f"**Observação:** {reg.get('observacao') or '-'}")
                st.write(f"**Responsável:** {reg.get('responsavel') or '-'}")

                col_e, col_r = st.columns(2)
                with col_e.popover("Editar"):
                    with st.form(f"editar_{reg['id_registro']}"):
                        novo_status = st.text_input("Status", value=reg["status"], key=f"s_{reg['id_registro']}")
                        nova_prio = st.text_input("Prioridade", value=reg["prioridade"], key=f"p_{reg['id_registro']}")
                        nova_obs = st.text_area("Observação", value=reg.get("observacao") or "", key=f"o_{reg['id_registro']}")
                        if st.form_submit_button("Salvar"):
                            if put(f"/registros/{reg['id_registro']}", json={
                                "status": novo_status,
                                "prioridade": nova_prio,
                                "observacao": nova_obs,
                            }):
                                st.success("Atualizado.")
                                st.rerun()

                if col_r.button("Remover", key=f"del_{reg['id_registro']}"):
                    if delete(f"/registros/{reg['id_registro']}"):
                        st.success("Removido.")
                        st.rerun()
    elif registros == []:
        st.info("Nenhum registro para este município ainda.")