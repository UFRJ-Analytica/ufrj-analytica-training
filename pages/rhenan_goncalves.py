from pathlib import Path
import pandas as pd
import streamlit as st
import requests
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

api = "http://127.0.0.1:8000/rhenan-goncalves"


# Servicos de API
def req_get(path):
    try:
        response = requests.get(f"{api}/{path}")
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API GET {path}: {e}")
        return None

def req_post(path, payload):
    try:
        response = requests.post(f"{api}/{path}", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição POST {path}: {e}")
        return None

def req_put(path, payload):
    try:
        response = requests.put(f"{api}/{path}", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição PUT {path}: {e}")
        return None

def req_delete(path):
    try:
        response = requests.delete(f"{api}/{path}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição DELETE {path}: {e}")
        return None

# Configuracao da Pagina
st.set_page_config(page_title="Dashboard IBGE & Gestão", page_icon=":bar_chart:", layout="wide")

# Cabeçalho Principal
st.title("Sistema de Acompanhamento Populacional - IBGE")
st.caption("Painel de visualização e gerenciamento de municípios, prioridades e situação")

# Abas principais
tab_dash, tab_registros, tab_gestao_muni = st.tabs([
    "Visualização de Dados", 
    "Prioridade & Situação", 
    "Gestão de Municípios"
])


with tab_dash:
    # KPI Totais
    data = req_get("totals")
    if data:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total de Municípios", f"{int(data['num_muni']):_}".replace("_", "."))
        col2.metric("Total de Estados", int(data["num_uf"]))
        col3.metric("População Total", f"{int(data['pop_total']):_}".replace("_", "."))
        col4.metric("Ano de Referência", int(data["ano"]))
        col5.metric("Município mais populoso", data["top_muni"])

    st.markdown("---")

    # Seção Municípios
    st.header("Municípios")
    muni_data_raw = req_get("muni")
    if muni_data_raw:
        data_muni = pd.DataFrame(muni_data_raw).rename(columns={'nome': "Cidade", 'pop': "População"})
        x = data_muni["População"]
        bins = np.logspace(np.log10(x.min()), np.log10(x.max()), 30)
        hist, edges = np.histogram(x, bins=bins)
        fig = go.Figure(go.Bar(x=np.sqrt(edges[:-1] * edges[1:]), y=hist, width=edges[1:] - edges[:-1]))
        fig.update_xaxes(type="log")
        fig.update_layout(yaxis_title="Número de Municípios", xaxis_title="População", title="Distribuição Populacional dos Municípios")
        st.plotly_chart(fig, use_container_width=True)

        lim = st.slider("Selecione o número de cidades no ranking", min_value=0, max_value=30, value=10)
        data_top = req_get(f"muni?limit={lim}")
        if data_top:
            df_top = pd.DataFrame(data_top).rename(columns={'nome': "Cidade"})
            df_top["População Formatada"] = df_top["pop"].apply(lambda val: f"{int(val):_}".replace("_", "."))

            fig_top = px.bar(df_top, x="Cidade", y="pop", title="População por Cidade", labels={"pop": "População", "Cidade": "Município"})
            st.plotly_chart(fig_top, use_container_width=True)
            st.table(df_top[["Cidade", "População Formatada"]].rename(columns={"População Formatada": "População"}))

    st.markdown("---")

    # Seção Estados
    st.header("Estados")
    opcoes = ["Sul", "Sudeste", "Centro-Oeste", "Nordeste", "Norte"]
    selecionados = st.pills("Selecione as Regiões", opcoes, selection_mode="multi")
    query_regs = ",".join(selecionados) if selecionados else ""
    data_uf = req_get(f"uf/?regs={query_regs}")
    if data_uf:
        df_uf = pd.DataFrame(data_uf).rename(columns={"nome": "Estado", "pop": "População"})
        fig_uf = px.bar(df_uf, x="Estado", y="População", title="População por Estado")
        st.plotly_chart(fig_uf, use_container_width=True)

    data_uf_stats = req_get("uf/stats")
    if data_uf_stats:
        df_stats = pd.DataFrame(data_uf_stats).rename(columns={"nome": "Estado", "count": "Número de Municípios", "avg": "População Média", "reg": "Região"})
        fig_scatter = px.scatter(df_stats, x="Número de Municípios", y="População Média", hover_name="Estado", size_max=30, color="Região", title="Municípios vs População Média por Estado")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # Seção Região
    st.header("Região")
    data_reg = req_get("reg")
    if data_reg:
        df_reg = pd.DataFrame(data_reg).rename(columns={'nome': "Região", 'pop': "População"})
        fig_pie = px.pie(df_reg, values="População", names="Região", title="População por Região")
        st.plotly_chart(fig_pie, use_container_width=True)

    data_porte = req_get("reg/porte")
    if data_porte:
        df_porte = (pd.DataFrame(data_porte).rename(columns={"nome": "Região", "peq": "Pequeno Porte", "med": "Médio Porte", "big": "Grande Porte"}))
        df_norm = df_porte.copy()
        cols = ["Pequeno Porte", "Médio Porte", "Grande Porte"]
        df_norm[cols] = df_norm[cols].apply(lambda c: c / c.max())
        fig_heat = px.imshow(df_norm.set_index("Região"), text_auto=False, color_continuous_scale="Blues", aspect="auto", title="Distribuição por Porte do Município por Região")
        fig_heat.update_traces(text=df_porte.set_index("Região").values, texttemplate="%{text}")
        st.plotly_chart(fig_heat, use_container_width=True)


with tab_registros:
    st.header("📋 Registros de Prioridade e Situação")
    st.caption("Gerenciamento de registros da nova tabela de municípios (Visualizar, Criar, Editar e Excluir)")

    sub_r1, sub_r2, sub_r3 = st.tabs(["👁️ Visualizar Registros", "➕ Novo Registro", "✏️ Editar / Excluir Registro"])

    # --- Sub-aba: Visualizar ---
    with sub_r1:
        registros = req_get("registros")
        if registros is not None:
            if len(registros) == 0:
                st.info("Nenhum registro cadastrado no momento. Cadastre um novo registro na aba ao lado.")
            else:
                df_reg_view = pd.DataFrame(registros)

                # Métricas rápidas
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total de Registros", len(df_reg_view))
                m2.metric("Prioridade Alta/Crítica", len(df_reg_view[df_reg_view["prioridade"].isin(["Alta", "Crítica"])]))
                m3.metric("Em Andamento", len(df_reg_view[df_reg_view["situacao"] == "Em Andamento"]))
                m4.metric("Concluídos", len(df_reg_view[df_reg_view["situacao"] == "Concluído"]))

                st.markdown("##### Filtros")
                f1, f2 = st.columns(2)
                prio_filter = f1.selectbox("Filtrar por Prioridade", ["Todas"] + sorted(list(df_reg_view["prioridade"].unique())))
                sit_filter = f2.selectbox("Filtrar por Situação", ["Todas"] + sorted(list(df_reg_view["situacao"].unique())))

                df_filtered = df_reg_view.copy()
                if prio_filter != "Todas":
                    df_filtered = df_filtered[df_filtered["prioridade"] == prio_filter]
                if sit_filter != "Todas":
                    df_filtered = df_filtered[df_filtered["situacao"] == sit_filter]

                st.dataframe(
                    df_filtered.rename(columns={
                        "id": "ID Registro",
                        "id_municipio": "ID Município",
                        "nome_municipio": "Município",
                        "prioridade": "Prioridade",
                        "situacao": "Situação"
                    }),
                    use_container_width=True
                )

    # --- Sub-aba: Criar ---
    with sub_r2:
        st.subheader("Cadastrar Novo Registro")
        muni_list = req_get("muni-lista")
        if muni_list:
            muni_options = {f"{m['nome_municipio']} ({m['nome_uf']}) - ID: {m['id_municipio']}": m['id_municipio'] for m in muni_list}

            with st.form("form_criar_registro"):
                muni_selected_str = st.selectbox("Selecione o Município", options=list(muni_options.keys()))
                prioridade_val = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"])
                situacao_val = st.selectbox("Situação", ["Planejado", "Em Andamento", "Concluído", "Suspenso"])
                submit_reg = st.form_submit_button("➕ Salvar Registro")

                if submit_reg:
                    target_id_muni = muni_options[muni_selected_str]
                    res = req_post("registros", {
                        "id_municipio": target_id_muni,
                        "prioridade": prioridade_val,
                        "situacao": situacao_val
                    })
                    if res:
                        st.success(f"Registro #{res['id']} cadastrado com sucesso para o município!")
                        st.rerun()

    # --- Sub-aba: Editar / Excluir ---
    with sub_r3:
        st.subheader("Editar ou Excluir Registro Existente")
        registros_edit = req_get("registros")
        if registros_edit:
            if len(registros_edit) == 0:
                st.info("Nenhum registro disponível para edição.")
            else:
                reg_dict = {
                    f"ID #{r['id']} - {r['nome_municipio']} | Prioridade: {r['prioridade']} | Situação: {r['situacao']}": r
                    for r in registros_edit
                }
                selected_label = st.selectbox("Selecione o Registro", list(reg_dict.keys()))
                curr_reg = reg_dict[selected_label]

                col_edit, col_del = st.columns([2, 1])

                with col_edit:
                    st.markdown("##### Atualizar Informações")
                    with st.form("form_editar_registro"):
                        new_prio = st.selectbox(
                            "Nova Prioridade",
                            ["Baixa", "Média", "Alta", "Crítica"],
                            index=["Baixa", "Média", "Alta", "Crítica"].index(curr_reg["prioridade"]) if curr_reg["prioridade"] in ["Baixa", "Média", "Alta", "Crítica"] else 0
                        )
                        new_sit = st.selectbox(
                            "Nova Situação",
                            ["Planejado", "Em Andamento", "Concluído", "Suspenso"],
                            index=["Planejado", "Em Andamento", "Concluído", "Suspenso"].index(curr_reg["situacao"]) if curr_reg["situacao"] in ["Planejado", "Em Andamento", "Concluído", "Suspenso"] else 0
                        )
                        btn_update_reg = st.form_submit_button("✏️ Atualizar Registro")

                        if btn_update_reg:
                            res_up = req_put(f"registros/{curr_reg['id']}", {
                                "prioridade": new_prio,
                                "situacao": new_sit
                            })
                            if res_up:
                                st.success(f"Registro #{curr_reg['id']} atualizado com sucesso!")
                                st.rerun()

                with col_del:
                    st.markdown("##### Remover Registro")
                    st.warning("Esta ação não poderá ser desfeita.")
                    if st.button("🗑️ Excluir Registro", type="primary"):
                        res_del = req_delete(f"registros/{curr_reg['id']}")
                        if res_del:
                            st.success(f"Registro #{curr_reg['id']} removido com sucesso!")
                            st.rerun()


with tab_gestao_muni:
    st.header("Gestão de Municípios")
    st.caption("Cadastrar novos municípios ou atualizar dados populacionais e localização de municípios existentes")

    sub_m1, sub_m2 = st.tabs(["➕ Criar Município", "✏️ Atualizar Município Existente"])

    # --- Sub-aba: Criar Município ---
    with sub_m1:
        st.subheader("Cadastrar Novo Município")
        estados_lista = req_get("estados-lista")
        if estados_lista:
            uf_names = [e["nome_uf"] for e in estados_lista]

            with st.form("form_criar_municipio"):
                nome_muni = st.text_input("Nome do Município", placeholder="Ex: Nova Friburgo")
                nome_uf_sel = st.selectbox("Estado (UF)", options=uf_names)
                pop_inicial = st.number_input("População Inicial (2025)", min_value=1, value=10000, step=1000)
                btn_cria_muni = st.form_submit_button("➕ Cadastrar Município")

                if btn_cria_muni:
                    if not nome_muni.strip():
                        st.error("O nome do município não pode estar em branco.")
                    else:
                        payload = {
                            "nome_municipio": nome_muni.strip(),
                            "nome_uf": nome_uf_sel,
                            "valor": int(pop_inicial)
                        }
                        res_muni = req_post("muni", payload)
                        if res_muni:
                            st.success(f"Município '{nome_muni}' criado com sucesso! (ID Gerado: {res_muni['id_municipio']})")
                            st.rerun()

    # --- Sub-aba: Atualizar Município ---
    with sub_m2:
        st.subheader("Atualizar Dados de Município Existente")
        all_munis = req_get("muni-lista")
        estados_lista = req_get("estados-lista")

        if all_munis and estados_lista:
            uf_names = [e["nome_uf"] for e in estados_lista]
            muni_map = {f"{m['nome_municipio']} ({m['nome_uf']}) - ID: {m['id_municipio']}": m for m in all_munis}

            selected_muni_label = st.selectbox("Selecione o Município para Editar", options=list(muni_map.keys()))
            muni_info = muni_map[selected_muni_label]

            with st.form("form_atualizar_municipio"):
                edit_nome_muni = st.text_input("Nome do Município", value=muni_info["nome_municipio"])
                curr_uf_idx = uf_names.index(muni_info["nome_uf"]) if muni_info["nome_uf"] in uf_names else 0
                edit_nome_uf = st.selectbox("Estado (UF)", options=uf_names, index=curr_uf_idx)
                edit_valor_pop = st.number_input("Nova População (2025)", min_value=1, value=10000, step=1000)
                btn_up_muni = st.form_submit_button("✏️ Salvar Alterações")

                if btn_up_muni:
                    payload_up = {
                        "nome_municipio": edit_nome_muni.strip(),
                        "nome_uf": edit_nome_uf,
                        "valor": int(edit_valor_pop)
                    }
                    res_up_muni = req_put(f"muni/{muni_info['id_municipio']}", payload_up)
                    if res_up_muni:
                        st.success(f"Município ID {muni_info['id_municipio']} atualizado com sucesso!")
                        st.rerun()