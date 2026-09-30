import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests

print("""

⠄⠄⠄⠄⠄⢀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣆⠄⠄⠄⠄
⠄⠄⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠄⠄⠄
⠄⠄⣾⣿⡿⠟⡋⠉⠛⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠉⠉⠙⠻⣿⣿⣇⠄⠄
⠄⢠⣿⡏⢰⣿⣿⡇⠄⠄⢸⣿⣿⣿⠿⠿⣿⣿⣿⠁⣾⣿⣷⠄⠄⠘⣿⣿⠄⠄
⠄⠸⣿⣇⠈⠉⠉⠄⠄⢀⣼⡿⠋⠄⠄⠄⠄⠙⢿⣄⠙⠛⠁⠄⠄⢠⣿⣿⠄⠄
⠄⠄⢿⣿⡇⠄⠄⠄⣶⣿⣿⢁⣤⣤⣤⣤⣤⣤⠄⣿⣷⠄⠄⠄⠈⢹⣿⡟⠄⠄
⠄⠄⠈⢿⡗⠄⠄⢸⣿⣿⣿⣶⣶⣶⣶⣶⣶⣶⣶⣿⣿⠄⠄⠄⠄⢸⡟⠄⠄⠄
⠄⠄⠄⠄⠳⡀⠄⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄⠄⠄⠌⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⠄⠄⠄⠄⠄⠄⠄⠄ 

""")

regioes_url = "http://127.0.0.1:8000/regioes"
estados_url = "http://127.0.0.1:8000/diogo-vieira/estados"
municipios_url = "http://127.0.0.1:8000/diogo-vieira/municipios"
estatisticas_url = "http://127.0.0.1:8000/diogo-vieira/estatisticas/resumo"
top_municipios_url = "http://127.0.0.1:8000/diogo-vieira/populacao/top-municipios"
populacao_regiao_url = "http://127.0.0.1:8000/diogo-vieira/populacao/por-regiao"
populacao_estado_url = "http://127.0.0.1:8000/diogo-vieira/populacao/por-uf"
populacao_distribuicao_url = "http://127.0.0.1:8000/diogo-vieira/populacao/distribuicao"
populacao_dispersao_url = "http://127.0.0.1:8000/diogo-vieira/populacao/dispersao-uf"
populacao_heatmap_url = "http://127.0.0.1:8000/diogo-vieira/populacao/heatmap-regiao-porte"
registros_url = "http://127.0.0.1:8000/diogo-vieira/registros"

st.set_page_config(page_title="SAP | Analytica Training", page_icon=":chart:", layout="wide")

st.title("Sistema de Acompanhamento Populacional")

st.divider()

response = requests.get(estatisticas_url)
if response.status_code == 200:
    data = response.json()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Estados", data["total_estados"])
    col2.metric("Total de Municípios", data["total_municipios"])
    col3.metric("População Total", data["populacao_total"])
    col4.metric("Ano de Referência", data["ano"])
else:
    st.error("Erro ao obter os dados do backend.")

st.divider()

col_tabela, _, col_grafico = st.columns([1, 0.15, 1])
with col_tabela:
    st.subheader("Municípios mais populosos do Brasil")
    quantidade_municipios = st.number_input("Top:", min_value=1, max_value=100, value=10, step=1)
    response = requests.get(top_municipios_url, params={"limit": quantidade_municipios})

    if response.status_code == 200:
        top_municipios = response.json()
        df = pd.DataFrame(top_municipios)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nome_municipio": st.column_config.TextColumn(
                    "Município"
                ),
                "populacao": st.column_config.ProgressColumn(
                    "População",
                    min_value=0,
                    max_value=int(df["populacao"].max()),
                    format="%d"
                )
            }
        )
    else:
        st.error("Erro ao obter os dados do backend.")

with col_grafico:
    st.subheader("População por região")
    response = requests.get(populacao_regiao_url)

    if response.status_code == 200:
        dados = response.json()
        df_regioes = pd.DataFrame(dados)
        fig = px.pie(
            df_regioes,
            names="nome_regiao",
            values="populacao_regional",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Erro ao obter os dados do backend.")

st.subheader("População por Estado")
regioes = {
    "Todas": None,
    "Norte": 1,
    "Nordeste": 2,
    "Sudeste": 3,
    "Sul": 4,
    "Centro-Oeste": 5
}
regiao_selecionada = st.selectbox(
    "Filtrar por região:",
    regioes.keys()
)

params = {}

if regioes[regiao_selecionada] is not None:
    params["id_regiao"] = regioes[regiao_selecionada]

response = requests.get(
    populacao_estado_url,
    params=params
)

if response.status_code == 200:
    dados = response.json()
    df_ufs = pd.DataFrame(dados)

    fig = px.bar(
        df_ufs,
        x="nome_uf",
        y="populacao_estadual",
        color="populacao_estadual",
        color_continuous_scale="Reds",
        labels={
            "nome_uf": "Estado",
            "populacao_estadual": "População"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.error("Erro ao obter os dados do backend.")

st.divider()

st.subheader("Distribuição da População dos Municípios")
response = requests.get(populacao_distribuicao_url)

if response.status_code == 200:
    dados = response.json()
    df_distribuicao = pd.DataFrame(dados)

    df_distribuicao["log_populacao"] = np.log10(
        df_distribuicao["populacao"]
    )

    fig = px.histogram(
        df_distribuicao,
        x="log_populacao",
        nbins=30
    )

    fig.update_traces(
        marker_color="#800026",
        marker_line_color="#111318",
        marker_line_width=1
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=[3, 4, 5, 6, 7],
        ticktext=[
            "1 mil",
            "10 mil",
            "100 mil",
            "1 milhão",
            "10 milhões"
        ],
        title="População do município"
    )

    fig.update_layout(
        yaxis_title="Quantidade de municípios"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.error("Erro ao obter os dados do backend.")

col1, _, col2 = st.columns([1, 0.15, 1])

with col1:
    st.subheader("Dispersão: Municípios x População Média")

    response = requests.get(populacao_dispersao_url)

    if response.status_code == 200:
        dados = response.json()
        df_dispersao = pd.DataFrame(dados)

        fig = px.scatter(
            df_dispersao,
            x="quantidade_municipios",
            y="populacao_media",
            color="nome_regiao",
            hover_name="nome_uf",
            log_y=True,
            labels={
                "quantidade_municipios": "Quantidade de municípios",
                "populacao_media": "População média",
                "nome_regiao": "Região"
            },
            hover_data={
                "quantidade_municipios": True,
                "populacao_media": ":,.0f",
                "nome_regiao": False
            }
        )

        fig.update_traces(
            marker=dict(size=10)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.error("Erro ao obter os dados do backend.")

with col2:
    st.subheader("Mapa de calor: Região x Porte")
    response = requests.get(populacao_heatmap_url)

    if response.status_code == 200:
        dados = response.json()
        df_heatmap = pd.DataFrame(dados)

        fig = px.density_heatmap(
            df_heatmap,
            x="porte",
            y="nome_regiao",
            z="quantidade_municipios",
            histfunc="sum",
            text_auto=True,
            category_orders={
                "porte": ["Pequeno", "Médio", "Grande"]
            },
            labels={
                "porte": "Porte do município",
                "nome_regiao": "Região",
                "quantidade_municipios": "Quantidade de municípios"
            },
            color_continuous_scale="Reds"
        )

        fig.update_coloraxes(
            colorbar_title="Quantidade<br>de municípios"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.error("Erro ao obter os dados do backend.")

st.divider()

col1, _, col2 = st.columns([1, 0.15, 1])

with col1:
    st.subheader("Gerenciar Municípios")
    tab_listar, tab_criar, tab_atualizar, tab_remover = st.tabs(
        ["Listar", "Cadastrar", "Atualizar", "Remover"]
    )

    response_municipios = requests.get(municipios_url)

    if response_municipios.status_code == 200:
        municipios = response_municipios.json()

        opcoes_municipios = {
            f"{m['nome_municipio']} - {m['id_municipio']}": m["id_municipio"]
            for m in municipios
        }

    else:
        municipios = []
        opcoes_municipios = {}
        st.error("Erro ao carregar os municípios.")

    with tab_listar:
        municipio_selecionado = st.selectbox(
            "Selecione o município",
            options=opcoes_municipios.keys(),
            key="municipio_listar"
        )

        if municipio_selecionado:
            id_municipio = opcoes_municipios[municipio_selecionado]

            response = requests.get(
                f"{municipios_url}/{id_municipio}"
            )

            if response.status_code == 200:
                dados = response.json()

                df_municipio = pd.DataFrame(dados)

                st.dataframe(
                    df_municipio,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "id_municipio": "ID",
                        "nome_municipio": "Município",
                        "nome_uf": "Estado",
                        "nome_regiao": "Região",
                        "populacao": st.column_config.NumberColumn(
                            "População",
                            format="%d"
                        )
                    }
                )

            elif response.status_code == 404:
                st.error("Município não encontrado.")

            else:
                st.error("Erro ao obter os dados do município.")

    with tab_criar:
        st.write("Cadastrar novo município")

        with st.form("form_criar_municipio"):
            nome = st.text_input("Nome do município")

            id_uf = st.number_input(
                "ID do estado",
                min_value=1,
                step=1
            )

            populacao = st.number_input(
                "População",
                min_value=0,
                step=1
            )

            cadastrar = st.form_submit_button("Cadastrar")

            if cadastrar:
                dados = {
                    "nome_municipio": nome,
                    "id_uf": int(id_uf),
                    "populacao": int(populacao)
                }

                response = requests.post(
                    municipios_url,
                    json=dados
                )

                if response.status_code == 200:
                    st.success("Município cadastrado com sucesso!")
                else:
                    st.error(
                        f"Erro ao cadastrar município: {response.text}"
                    )

    with tab_atualizar:
        municipio_selecionado = st.selectbox(
            "Município",
            options=opcoes_municipios.keys(),
            key="municipio_atualizar"
        )

        id_municipio = opcoes_municipios[municipio_selecionado]

        alterar_nome = st.checkbox("Alterar nome")
        novo_nome = st.text_input(
            "Novo nome",
            disabled=not alterar_nome
        )

        alterar_estado = st.checkbox("Alterar estado")
        novo_id_uf = st.number_input(
            "Novo ID do estado",
            min_value=1,
            step=1,
            disabled=not alterar_estado
        )

        alterar_populacao = st.checkbox("Alterar população")
        nova_populacao = st.number_input(
            "Nova população",
            min_value=0,
            step=1,
            disabled=not alterar_populacao
        )

        if st.button("Atualizar município"):

            dados = {}

            if alterar_nome:
                dados["nome_municipio"] = novo_nome

            if alterar_estado:
                dados["id_uf"] = int(novo_id_uf)

            if alterar_populacao:
                dados["populacao_atualizada"] = int(nova_populacao)

            if not dados:
                st.warning("Selecione pelo menos um campo para atualizar.")

            else:
                response = requests.put(
                    f"{municipios_url}/{id_municipio}",
                    json=dados
                )

                if response.status_code == 200:
                    st.success("Município atualizado com sucesso!")

                elif response.status_code == 404:
                    st.error("Município não encontrado.")

                else:
                    st.error(response.text)

    with tab_remover:
        municipio_selecionado = st.selectbox(
            "Município",
            options=opcoes_municipios.keys(),
            key="municipio_remover"
        )

        id_municipio = opcoes_municipios[municipio_selecionado]

        confirmar = st.checkbox(
            "Confirmo que desejo remover este município"
        )

        if st.button("Remover município"):

            if not confirmar:
                st.warning("Confirme a remoção.")

            else:
                response = requests.delete(
                    f"{municipios_url}/{id_municipio}"
                )

                if response.status_code == 200:
                    st.success("Município removido com sucesso!")

                elif response.status_code == 404:
                    st.error("Município não encontrado.")

                else:
                    st.error(response.text)

with col2:
    st.subheader("Cadastro de Registros")

    tab_criar, tab_listar, tab_editar, tab_remover = st.tabs([
        "Criar",
        "Listar",
        "Editar",
        "Remover"
    ])

    with tab_criar:

        municipio_selecionado = st.selectbox(
            "Município",
            options=opcoes_municipios.keys(),
            key="municipio_criar"
        )

        observacao = st.text_area(
            "Observação",
            placeholder="Digite uma observação sobre o município...",
            key="observacao_criar"
        )

        if st.button("Criar registro"):

            if not observacao.strip():
                st.warning("Digite uma observação.")

            else:
                id_municipio = opcoes_municipios[municipio_selecionado]

                response = requests.post(
                    f"{municipios_url}/{id_municipio}/registros",
                    params={
                        "observacao": observacao
                    }
                )

                if response.status_code == 200:
                    st.success("Registro criado com sucesso!")

                elif response.status_code == 404:
                    st.error("Município não encontrado.")

                else:
                    st.error(response.text)

    with tab_listar:

        municipio_selecionado = st.selectbox(
            "Município",
            options=opcoes_municipios.keys(),
            key="registros_listar"
        )

        if municipio_selecionado:

            id_municipio = opcoes_municipios[municipio_selecionado]

            response = requests.get(
                f"{municipios_url}/{id_municipio}/registros"
            )

            if response.status_code == 200:

                registros = pd.DataFrame(response.json())

                st.dataframe(
                    registros,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "id_registro": "ID",
                        "id_municipio": "ID Município",
                        "data_registro": "Data",
                        "observacao": st.column_config.TextColumn(
                            "Observação",
                            width="large"
                        )
                    }
                )

            elif response.status_code == 404:
                st.info("Nenhum registro encontrado para este município.")

            else:
                st.error(response.text)

    with tab_editar:

        municipio_selecionado = st.selectbox(
            "Município",
            options=opcoes_municipios.keys(),
            key="municipio_editar"
        )

        if municipio_selecionado:

            id_municipio = opcoes_municipios[municipio_selecionado]

            response = requests.get(
                f"{municipios_url}/{id_municipio}/registros"
            )

            if response.status_code == 200:

                registros = response.json()

                opcoes_registros = {
                    f"Registro {r['id_registro']} - {r['observacao'][:50]}":
                        r
                    for r in registros
                }

                registro_selecionado = st.selectbox(
                    "Registro",
                    options=opcoes_registros.keys()
                )

                registro = opcoes_registros[registro_selecionado]

                nova_observacao = st.text_area(
                    "Observação",
                    value=registro["observacao"]
                )

                if st.button("Atualizar registro"):

                    response_put = requests.put(
                        f"{registros_url}/{registro['id_registro']}",
                        params={
                            "observacao": nova_observacao
                        }
                    )

                    if response_put.status_code == 200:
                        st.success("Registro atualizado com sucesso!")

                    elif response_put.status_code == 404:
                        st.error("Registro não encontrado.")

                    else:
                        st.error(response_put.text)

            elif response.status_code == 404:
                st.info("Este município não possui registros.")

    with tab_remover:

        municipio_selecionado = st.selectbox(
            "Município",
            options=opcoes_municipios.keys(),
            key="municipio_remover_registro"
        )

        if municipio_selecionado:

            id_municipio = opcoes_municipios[municipio_selecionado]

            response = requests.get(
                f"{municipios_url}/{id_municipio}/registros"
            )

            if response.status_code == 200:

                registros = response.json()

                opcoes_registros = {
                    f"Registro {r['id_registro']} - {r['observacao'][:50]}":
                        r
                    for r in registros
                }

                registro_selecionado = st.selectbox(
                    "Registro",
                    options=opcoes_registros.keys(),
                    key="registro_remover"
                )

                registro = opcoes_registros[registro_selecionado]

                st.write("Observação:")
                st.info(registro["observacao"])

                confirmar = st.checkbox(
                    "Confirmo que desejo remover este registro"
                )

                if st.button("Remover registro"):

                    if not confirmar:
                        st.warning("Confirme a remoção.")

                    else:
                        response_delete = requests.delete(
                            f"{registros_url}/{registro['id_registro']}"
                        )

                        if response_delete.status_code == 200:
                            st.success("Registro removido com sucesso!")

                        elif response_delete.status_code == 404:
                            st.error("Registro não encontrado.")

                        else:
                            st.error(response_delete.text)

            elif response.status_code == 404:
                st.info("Este município não possui registros.")