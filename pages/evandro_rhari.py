from pathlib import Path

import streamlit as st

import pandas as pd

import json

from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from requests import request


prefix = "http://backend:8000/evandro-rhari"


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
def mapa_porte(porte_df: pd.DataFrame):
    with open('./data/grandes_regioes_json.geojson') as file:
        mapa = json.load(file)
    porte_df = porte_df.sort_values('porte')
    fig = px.choropleth(porte_df, geojson=mapa, locations='id_regiao', scope='south america', color='porte', hover_data=['nome_regiao'], featureidkey="properties.ID", color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
    st.plotly_chart(fig)


def write_cool_emphasis(title, text):
    st.markdown(f"<p style='margin:0; padding:0'>{title}</p>\n<p style='font-size:2rem; margin:0; padding:0'> {text}</p> ", unsafe_allow_html=True)


def kpis_sub_collumn(col_dict):
    titles = list(col_dict.keys())
    texts = list(col_dict.values())
    cols = st.columns(len(col_dict))
    for i in range(0, len(cols)):
        with cols[i]:
            write_cool_emphasis(titles[i], kpis[texts[i]])


st.title("População Brasileira | IBGE")
st.caption("Informações em diferentes perspectivas sobre a população brasileira | Todos os dados vieram do IBGE. | Evandro Rhari")


kpis = get_request("/estatisticas/resumo")
kpis = kpis.loc[0]


bigcols = st.columns(2)
with bigcols[0]:
    kpis_sub_collumn({
        "Municipios": 'total_municipio',
        "Estados": 'total_estado',
        "Regioes": 'total_regioes',
    })
with bigcols[1]:
    kpis_sub_collumn(col_dict = {
        "Populacao: ": 'populacao_total',
        "Ano": 'ano'
    })



tabs = st.tabs(['Top Municipios', 'População', 'Porte', 'Registros'])

with tabs[0]:
    st.write("## Top Município em População")

    topn = st.number_input("Quantidade de municipios:", step=1, value=5, min_value=1)

    col1, col2 = st.columns(2)
    with col1:
        df_topn = request_and_write(f"/populacao/top-municipios?limit={topn}", ['nome_municipio', 'População'])
    with col2:
        st.bar_chart(df_topn, x='nome_municipio', y='População', sort='População')


with tabs[1]:
    st.write("## Dados sobre população")

    pop_reg = get_request("/populacao/por-regiao", ['nome_regiao', 'populacao'])
    pop_uf  = get_request("/populacao/por-uf", ['nome_uf', 'populacao_total'])

    col1, col2 = st.columns(2)
    with col1:
        st.write("### População por região")
        donut_plot(pop_reg, 'nome_regiao', 'populacao')
    with col2:
        st.write("### População por estado")
        donut_plot(pop_uf, 'nome_uf', 'populacao_total')
    col1, col2 = st.columns(2)
    with col1:
        st.write(pop_reg)
    with col2:
        st.write(pop_uf)


    st.write("### Distribuição da população")
    distribuicao_pop = request_and_write("/populacao/distribuicao").sort_values('populacao')

    st.write("### Dispersão da população")
    dispersao_pop = request_and_write("/populacao/dispersao-uf")
    dispersao_pop = dispersao_pop.drop(dispersao_pop[dispersao_pop['nome_uf'] == "Distrito Federal"].index, axis=0)
    st.scatter_chart(dispersao_pop, y='quantidade_municipios', x='populacao_media', color='nome_uf')
    st.caption("Distro federal foi retirado por ser um outlier")


with tabs[2]:
    st.write("### Porte Regional ")
    st.caption("Metrica: 0 ⊢ 0.8\*media -> Pequeno; 0.8\*media ⊢ 1.2\*media -> Medio; 1.2\*media >= -> Grande")

    col1, col2 = st.columns(2)

    with col1:
        porte_df = request_and_write("/populacao/heatmap-regiao-porte")

    porte_df['id_mapa'] = (porte_df['id_regiao']+1).astype('str')
    porte_df['nome_regiao'] = porte_df['nome_regiao'].str.strip()

    with col2:
        mapa_porte(porte_df)


with tabs[3]:
    st.write("## Gestão de Registros IBGE")
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


