"""Painel Streamlit"""

import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_URL = os.getenv("LUCAS_CONT_API_URL", "http://127.0.0.1:8000/lucas-cont")
st.set_page_config(page_title="Painel populacional", page_icon=":bar_chart:", layout="wide")
st.title("Painel populacional")
st.caption("Indicadores derivados do banco normalizado do IBGE.")


def get_json(path: str, **params):
    response = requests.get(f"{API_URL}/{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


try:
    resumo = get_json("kpis")
except requests.RequestException as exc:
    st.error(f"API indisponível: {exc}")
    st.stop()

colunas = st.columns(4)
colunas[0].metric("Municípios", f"{resumo['municipios']:,}".replace(",", "."))
colunas[1].metric("Estados", resumo["estados"])
colunas[2].metric("Regiões", resumo["regioes"])
colunas[3].metric("Ano de referência", resumo["ano"] or "N/D")

limite = st.slider("Quantidade de municípios em destaque", 5, 25, 10)
try:
    dados = get_json("destaques", limite=limite)
except requests.RequestException as exc:
    st.warning(f"Não foi possível carregar os destaques: {exc}")
else:
    tabela = pd.DataFrame(dados)
    if tabela.empty:
        st.info("Não há dados populacionais disponíveis.")
    else:
        esquerda, direita = st.columns((1.1, 1))
        with esquerda:
            st.dataframe(tabela, use_container_width=True, hide_index=True)
        with direita:
            grafico = px.bar(
                tabela,
                x="nome_municipio",
                y="populacao",
                color="sigla_uf",
                title="Municípios mais populosos",
            )
            st.plotly_chart(grafico, use_container_width=True)
