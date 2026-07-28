from pathlib import Path

import streamlit as st

import pandas as pd

import json

from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from requests import request


prefix = "http://127.0.0.1:8000/evandro-rhari"


def get_request(url, columns=[]):
    df = pd.read_json(prefix+url)
    if columns:
        df = df[columns]
    return df


def request_and_write(url, columns=[]):
    df = get_request(url, columns)
    st.write(df)
    return df


def donut_plot(data, labels, values, hole=0.5):
    fig = px.pie(data, names=labels, values=values, hole=hole, color_discrete_sequence=px.colors.sequential.Aggrnyl)
    st.plotly_chart(fig)
    return fig


def hist_plot(data, x, y):
    fig = px.histogram(data, x=x, y=y)
    st.plotly_chart(fig)
    return fig


def get_municipio_id(municipio, municipios=None):
    municipio_id = municipios[municipios['nome_municipio'] == municipio]['id_municipio'].reset_index()['id_municipio']
    if municipio_id.empty:
        st.write("Erro. Municipio não encontrado")
    else:
        return int(municipio_id[0])


@st.cache_data
def mapa_porte():
    with open('./backend/dados/grandes_regioes_json.geojson') as file:
        mapa = json.load(file)
    fig = px.choropleth(porte_df, geojson=mapa, locations='id_regiao', scope='south america', color='porte', hover_data=['nome_regiao'], featureidkey="properties.ID", color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
    st.plotly_chart(fig)



st.title("Dados IBGE | Evandro Rhari")
st.caption("Base inicial em Streamlit para apresentar equipe, projetos e frente de treino.")


st.write("KPIs:")
request_and_write("/estatisticas/resumo")


tabs = st.tabs(['Top Municipios', 'População', 'Porte', 'Registros'])

with tabs[0]:
    topn = st.number_input("Quantidade de municipios:", step=1, value=5, min_value=1)

    col1, col2 = st.columns(2)
    with col1:
        df_topn = request_and_write(f"/populacao/top-municipios?limit={topn}", ['nome_municipio', 'População'])
    with col2:
        st.bar_chart(df_topn, x='nome_municipio', y='População', sort='População')


with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.write("População por região")
        pop_reg = request_and_write("/populacao/por-regiao", ['nome_regiao', 'populacao'])
    with col2:
        st.write("População por estado")
        pop_uf = request_and_write("/populacao/por-uf", ['nome_uf', 'populacao_total'])
    col1, col2 = st.columns(2)
    with col1:
        donut_plot(pop_reg, 'nome_regiao', 'populacao')
    with col2:
        donut_plot(pop_uf, 'nome_uf', 'populacao_total')


    st.write("Distribuição da população")
    distribuicao_pop = request_and_write("/populacao/distribuicao")


    st.write("Dispersão da população")
    dispersao_pop = request_and_write("/populacao/dispersao-uf")
    st.scatter_chart(dispersao_pop, y='quantidade_municipios', x='populacao_media', color='nome_uf')


with tabs[2]:
    col1, col2 = st.columns(2)

    with col1:
        st.write("Porte")
        porte_df = request_and_write("/populacao/heatmap-regiao-porte")

    porte_df['id_mapa'] = (porte_df['id_regiao']+1).astype('str')
    porte_df['nome_regiao'] = porte_df['nome_regiao'].str.strip()

    with col2:
        mapa_porte()


with tabs[3]:
    crud = st.tabs(['Criar', 'Encontrar', 'Editar', 'Remover'])
    with crud[0]:
        municipios = get_request('/municipios')
        with st.form("Criar Registro"):
            col1, col2 = st.columns(2)
            with col1:
                status = st.text_input("Status Atual:")
                prioridade = st.selectbox("Prioridade: ", ['Baixa', 'Media', 'Alta'])
            with col2:
                responsavel = st.text_input("Responsável: ")
                municipio = st.selectbox("Municipio: ", municipios['nome_municipio'])
            enviar = st.form_submit_button("Enviar")

        if enviar:
            municipio_id = municipios[municipios['nome_municipio'] == municipio]['id_municipio'].reset_index()['id_municipio']
            if municipio_id.empty:
                st.write("Erro. Municipio não encontrado")
            else:
                municipio_id = int(municipio_id[0])
                data = {"status_atual": status, 
                        "prioridade": prioridade,
                        "responsavel": responsavel,
                        "id_municipio": municipio_id 
                        }
                r = request('POST', prefix+f'/municipios/{municipio_id}/registros', json=data)
                if r.status_code != 200:
                    st.write("Algo deu errado.")
                else:
                    st.write("Sucesso!")

    with crud[1]:
        municipios = get_request('/municipios')
        municipio = st.selectbox("Municipio: ", municipios['nome_municipio'])
        municipio_id = get_municipio_id(municipio, municipios)
        if municipio_id:
            request_and_write(f"/municipios/{municipio_id}/registros")

    with crud[2]:
        registro_id = st.number_input("Id Registro", step=1)

        municipios = get_request('/municipios')
        with st.form("Editar Registro"):
            col1, col2 = st.columns(2)
            with col1:
                status = st.text_input("Status Atual:")
                prioridade = st.selectbox("Prioridade: ", ['Baixa', 'Media', 'Alta'])
            with col2:
                responsavel = st.text_input("Responsável: ")
                municipio = st.selectbox("Municipio: ", municipios['nome_municipio'])
            enviar = st.form_submit_button("Enviar")

        if enviar:
            municipio_id = municipios[municipios['nome_municipio'] == municipio]['id_municipio'].reset_index()['id_municipio']
            if municipio_id.empty:
                st.write("Erro. Municipio não encontrado")
            else:
                municipio_id = int(municipio_id[0])
                data = {"id_cadastro_municipal": registro_id,
                        "status_atual": status, 
                        "prioridade": prioridade,
                        "responsavel": responsavel,
                        "id_municipio": municipio_id 
                        }
                print(f"\n\n\n\n\n\n\n{data}\n\n\n\n\n\n\n\n")
                r = request('PUT', prefix+f'/registros/{registro_id}', json=data)
                if r.status_code != 200:
                    st.write("Algo deu errado.")
                else:
                    st.write("Sucesso!")

    with crud[3]:
        registro_id = st.number_input("Id Registro Deletar", step=1)
        deletar = st.button("Deletar")

        if deletar:
            r = request('DELETE', prefix+f'/registros/{registro_id}')
            if r.status_code != 200:
                st.write("Algo deu errado.")
            else:
                st.write("Sucesso!")


