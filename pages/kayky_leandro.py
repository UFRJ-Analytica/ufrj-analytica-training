import streamlit as st
import requests

API = "http://127.0.0.1:8000/kayky-leandro"

st.title("Sistema de Acompanhamento Populacional")

#KPIS
try:
    resposta = requests.get(f"{API}/estatisticas/resumo")

    if resposta.status_code == 200:
        dados = resposta.json()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Municípios",
            dados["total_municipios"]
        )

        col2.metric(
            "Estados",
            dados["total_estados"]
        )

        col3.metric(
            "População",
            f'{dados["populacao_total"]:,}'
        )

        st.metric(
            "Município mais populoso",
            dados["municipio_mais_populoso"]
        )

        st.metric(
            "Ano de referência",
            dados["ano_referencia"]
        )

    else:
        st.error("Erro ao consultar a API.")

except:
    st.error("A API não está rodando.")

#TOP MUNICIPIOS
st.header("Top Municípios")

top = requests.get(f"{API}/populacao/top-municipios").json()

limite = st.slider(
    "Quantidade de municípios",
    5,
    20,
    10
)
st.dataframe(top)
st.bar_chart(
    data=top,
    x="nome_municipio",
    y="populacao"
)

#POPULAÇÃO POR REGIÃO
st.header("População por Região")

regioes = requests.get(f"{API}/populacao/por-regiao").json()

st.dataframe(regioes)
st.bar_chart(
    data=regioes,
    x="nome_regiao",
    y="populacao_total"
)

#POPULAÇÃO POR UF
st.header("População por Estado")

ufs = requests.get(f"{API}/populacao/por-uf").json()

st.dataframe(ufs)
st.bar_chart(
    data=ufs,
    x="nome_uf",
    y="populacao_total"
)

#HISTOGRAMA DA DISTRIBUIÇÃO POPULACIONAL
dist = requests.get(f"{API}/populacao/distribuicao").json()

st.bar_chart(dist)

#SCATTER DA DISPERSÃO POPULACIONAL
scatter = requests.get(f"{API}/populacao/dispersao-uf").json()

st.dataframe(scatter)

#HEATMAP REGIÃO PORTE
heat = requests.get(f"{API}/populacao/heatmap-regiao-porte").json()

st.dataframe(heat)

#CADASTRO MUNICIPIO
st.header("Novo Município")

nome = st.text_input("Nome")
uf = st.number_input("ID da UF", min_value=1)
pop = st.number_input("População", min_value=0)

if st.button("Cadastrar"):
    requests.post(
        f"{API}/municipios",
        json={
            "nome": nome,
            "id_uf": uf,
            "populacao": pop
        }
    )
    st.success("Município cadastrado!")

#LISTAR MUNICIPIOS
st.header("Municípios")

municipios = requests.get(f"{API}/municipios").json()

st.dataframe(municipios)

#ATUALIZAR MUNICIPIOS
st.header("Atualizar Município")

id_municipio = st.number_input(
    "ID do Município",
    min_value=1,
    step=1,
    key="id_update"
)

novo_nome = st.text_input(
    "Novo nome",
    key="nome_update"
)

nova_uf = st.number_input(
    "Nova UF",
    min_value=1,
    key="uf_update"
)

nova_pop = st.number_input(
    "Nova população",
    min_value=0,
    key="pop_update"
)

if st.button("Atualizar Município"):
    requests.put(
        f"{API}/municipios/{id_municipio}",
        json={
            "nome": novo_nome,
            "id_uf": nova_uf,
            "populacao": nova_pop
        }
    )
    st.success("Município atualizado!")

#DELETAR MUNICIPIOS
st.header("Remover Município")

id_delete = st.number_input(
    "ID para remover",
    min_value=1,
    key="delete"
)

if st.button("Excluir Município"):
    requests.delete(f"{API}/municipios/{id_delete}")
    st.success("Município removido!")

#CADASTRO REGISTROS
st.header("Novo Registro")

municipio = st.number_input("ID Município", min_value=1)
obs = st.text_area("Observação")

if st.button("Salvar Registro"):
    requests.post(
        f"{API}/municipios/{municipio}/registros",
        json={
            "observacao": obs
        }
    )
    st.success("Registro salvo!")

# CRIAR REGISTROS
st.header("Registros")

id_mun = st.number_input(
    "Município",
    min_value=1,
    key="listar"
)

if st.button("Listar Registros"):

    registros = requests.get(
        f"{API}/municipios/{id_mun}/registros"
    ).json()

    st.dataframe(registros)

# ATUALIZAR REGISTROS
st.header("Atualizar Registro")

id_reg = st.number_input(
    "ID Registro",
    min_value=1,
    key="reg_update"
)

nova_obs = st.text_area(
    "Nova observação",
    key="obs_update"
)

if st.button("Atualizar Registro"):

    requests.put(
        f"{API}/registros/{id_reg}",
        json={
            "observacao": nova_obs
        }
    )

    st.success("Registro atualizado!")

# DELETAR REGISTROS
st.header("Remover Registro")

id_reg_del = st.number_input(
    "Registro",
    min_value=1,
    key="reg_delete"
)

if st.button("Excluir Registro"):

    requests.delete(
        f"{API}/registros/{id_reg_del}"
    )

    st.success("Registro removido!")
