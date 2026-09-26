import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Acompanhamento Populacional",
    layout="wide"
)


st.title("Sistema de Acompanhamento Populacional")
st.write("Análise e acompanhamento dos municípios brasileiros")


def api_get(endpoint, params=None):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            params=params,
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException:
        st.error(
            "Não foi possível conectar à API. "
            "Verifique se o servidor está rodando."
        )
        return None


# Análise

st.header("Análise populacional")

resumo = api_get("/mariana-freitas/estatisticas/resumo")

if resumo:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Municípios",
            resumo["total_municipios"]
        )

    with col2:
        st.metric(
            "Estados",
            resumo["total_estados"]
        )

    with col3:
        st.metric(
            "População total",
            f'{resumo["populacao_total"]:,}'.replace(",", ".")
        )

    with col4:
        st.metric(
            "Ano",
            resumo["ano_referencia"]
        )

    with col5:
        st.metric(
            "Mais populoso",
            resumo["municipio_mais_populoso"]
        )


# Top N municipios

st.subheader("Municípios mais populosos")

quantidade = st.slider(
    "Quantidade de municípios",
    min_value=5,
    max_value=20,
    value=10
)

top_municipios = api_get(
    "/mariana-freitas/populacao/top-municipios",
    params={"limit": quantidade}
)

if top_municipios:
    df_top = pd.DataFrame(top_municipios)

    st.dataframe(
        df_top,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        df_top.set_index("nome_municipio")["populacao"]
    )


# População por região

st.subheader("População por região")

populacao_regiao = api_get(
    "/mariana-freitas/populacao/por-regiao"
)

if populacao_regiao:
    df_regiao = pd.DataFrame(populacao_regiao)

    st.dataframe(
        df_regiao,
        use_container_width=True,
        hide_index=True
    )

    st.plotly_chart(
        {
            "data": [
                {
                    "labels": df_regiao["nome_regiao"].tolist(),
                    "values": df_regiao["populacao_total"].tolist(),
                    "type": "pie"
                }
            ],
            "layout": {
                 "title": "População por região"
            }
        },
        use_container_width=True
    )

# População por estado

st.subheader("População por estado")

opcoes_regiao = {
    "Todas as regiões": None,
    "Norte": 1,
    "Nordeste": 2,
    "Sudeste": 3,
    "Sul": 4,
    "Centro-Oeste": 5
}

regiao_selecionada = st.selectbox(
    "Filtrar por região",
    list(opcoes_regiao.keys())
)

id_regiao = opcoes_regiao[regiao_selecionada]

populacao_uf = api_get(
    "/mariana-freitas/populacao/por-uf",
    params={"id_regiao": id_regiao}
)

if populacao_uf:
    df_uf = pd.DataFrame(populacao_uf)

    st.bar_chart(
        df_uf.set_index("sigla_uf")["populacao"]
    )


# Distribuição da população

st.subheader("Distribuição da população")

distribuicao = api_get(
    "/mariana-freitas/populacao/distribuicao"
)

if distribuicao:
    df_distribuicao = pd.DataFrame(distribuicao)

    st.plotly_chart(
        {
            "data": [
                {
                    "x": df_distribuicao["populacao"].tolist(),
                    "type": "histogram",
                    "nbinsx": 30
                }
            ],
            "layout": {
                "title": "Distribuição da população dos municípios",
                "xaxis": {
                    "title": "População"
                },
                "yaxis": {
                    "title": "Quantidade de municípios"
                }
            }
        },
        use_container_width=True
    )


# Dispersão: Municípios × população média por estado

st.subheader("Municípios × população média por estado")

dispersao = api_get(
    "/mariana-freitas/populacao/dispersao-uf"
)

if dispersao:
    df_dispersao = pd.DataFrame(dispersao)

    # Região de cada estado
    regioes_uf = {
        "AC": "Norte",
        "AP": "Norte",
        "AM": "Norte",
        "PA": "Norte",
        "RO": "Norte",
        "RR": "Norte",
        "TO": "Norte",

        "AL": "Nordeste",
        "BA": "Nordeste",
        "CE": "Nordeste",
        "MA": "Nordeste",
        "PB": "Nordeste",
        "PE": "Nordeste",
        "PI": "Nordeste",
        "RN": "Nordeste",
        "SE": "Nordeste",

        "DF": "Centro-Oeste",
        "GO": "Centro-Oeste",
        "MT": "Centro-Oeste",
        "MS": "Centro-Oeste",

        "ES": "Sudeste",
        "MG": "Sudeste",
        "RJ": "Sudeste",
        "SP": "Sudeste",

        "PR": "Sul",
        "RS": "Sul",
        "SC": "Sul"
    }

    df_dispersao["regiao"] = df_dispersao["sigla_uf"].map(regioes_uf)

    fig = go.Figure()

    for regiao in [
        "Norte",
        "Nordeste",
        "Centro-Oeste",
        "Sudeste",
        "Sul"
    ]:
        dados_regiao = df_dispersao[
            df_dispersao["regiao"] == regiao
        ]

        fig.add_trace(
            go.Scatter(
                x=dados_regiao["quantidade_municipios"],
                y=dados_regiao["populacao_media"],
                mode="markers",
                name=regiao,
                text=dados_regiao["sigla_uf"],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Municípios: %{x}<br>"
                    "População média: %{y:,.0f}"
                    "<extra>" + regiao + "</extra>"
                ),
                marker={
                    "size": 9
                }
            )
        )

    fig.update_layout(
        title="Quantidade de municípios × população média",
        xaxis_title="Quantidade de municípios",
        yaxis_title="População média",
        legend_title="Região"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# Mapa de calor: Municípios por região e porte

st.subheader("Municípios por região e porte")

heatmap = api_get(
    "/mariana-freitas/populacao/heatmap-regiao-porte"
)

if heatmap:
    df_heatmap = pd.DataFrame(heatmap)

    fig_heatmap = {
        "data": [
            {
                "x": df_heatmap["porte"].tolist(),
                "y": df_heatmap["nome_regiao"].tolist(),
                "z": df_heatmap["quantidade"].tolist(),
                "type": "heatmap",
                "text": df_heatmap["quantidade"].tolist(),
                "texttemplate": "%{text}"
            }
        ],
        "layout": {
            "title": "Quantidade de municípios por região e porte",
            "xaxis": {
                "title": "Porte"
            },
            "yaxis": {
                "title": "Região"
            }
        }
    }

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )


# Cadastro de município

st.header("Cadastro de município")

st.subheader("Criar novo município")

with st.form("form_criar_municipio"):

    nome_municipio = st.text_input(
        "Nome do município"
    )

    id_uf = st.number_input(
        "ID da UF",
        min_value=1,
        step=1
    )

    populacao = st.number_input(
        "População",
        min_value=0,
        step=1
    )

    enviar = st.form_submit_button(
        "Cadastrar município"
    )

    if enviar:
        dados = {
            "nome_municipio": nome_municipio,
            "id_uf": id_uf,
            "populacao": populacao
        }

        resposta = requests.post(
            f"{API_URL}/mariana-freitas/municipios",
            json=dados
        )

        if resposta.status_code in [200, 201]:
            st.success("Município cadastrado com sucesso!")
            st.rerun()
        else:
            st.error(
                f"Erro ao cadastrar município: {resposta.text}"
            )


# Listar municipios

st.subheader("Municípios cadastrados")

municipios_cadastrados = api_get(
    "/mariana-freitas/municipios"
)

if municipios_cadastrados:
    st.dataframe(
        municipios_cadastrados,
        use_container_width=True
    )
else:
    st.info("Nenhum município cadastrado.")


# Editar ou remover município

st.subheader("Editar ou remover município")

municipios = api_get(
    "/mariana-freitas/municipios"
)

distribuicao = api_get(
    "/mariana-freitas/populacao/distribuicao"
)

populacoes = {
    m["nome_municipio"]: m["populacao"]
    for m in distribuicao
}

if municipios:

    opcoes_municipios = {
        f'{m["nome_municipio"]} (ID {m["id_municipio"]})': m
        for m in municipios
    }

    municipio_selecionado = st.selectbox(
        "Selecione um município",
        list(opcoes_municipios.keys())
    )

    municipio = opcoes_municipios[municipio_selecionado]

    id_municipio = municipio["id_municipio"]

    novo_nome = st.text_input(
        "Nome",
        value=municipio["nome_municipio"]
    )

    nova_uf = st.number_input(
        "ID da UF",
        min_value=1,
        value=int(municipio["id_municipio"]),
        step=1
    )

    nova_populacao = st.number_input(
        "População",
        min_value=0,
        value=int(populacoes.get(municipio["nome_municipio"], 0)),
        step=1
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Salvar alterações"):

            dados = {
                "nome_municipio": novo_nome,
                "id_municipio": novo_municipio,
                "populacao": nova_populacao
            }

            resposta = requests.put(
                f"{API_URL}/mariana-freitas/municipios/{id_municipio}",
                json=dados
            )

            if resposta.status_code in [200, 204]:
                st.success(
                    "Município atualizado com sucesso!"
                )
                st.rerun()
            else:
                st.error(
                    f"Erro ao atualizar: {resposta.text}"
                )

    with col2:
        if st.button("Remover município"):

            resposta = requests.delete(
                f"{API_URL}/mariana-freitas/municipios/{id_municipio}"
            )

            if resposta.status_code in [200, 204]:
                st.success(
                    "Município removido com sucesso!"
                )
                st.rerun()
            else:
                st.error(
                    f"Erro ao remover: {resposta.text}"
                )

else:
    st.warning("Nenhum município encontrado.")