import streamlit as st
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

base_url = "http://127.0.0.1:8000/marcelo-borges"

# ===================
# kpi: medidas resumo
# ===================
resumo = requests.get(base_url+"/estatisticas/resumo").json()[0]
st.header("Estatísticas Resumo")
left, right = st.columns(2)
with left:
    st.write("Quantidade de Municípios: ", resumo["municipios"])
    st.write("Quantidade de Estados: ", resumo["estados"])
    st.write(f"População Total: ", resumo["populacao_total"])
with right:
    st.write("Ano do Censo: ", resumo["ano"])
    st.write(f"Maior Município: **{resumo["maior_municipio"]}**")
st.divider()

# ===============================
# Top N municípios mais populosos
# ===============================
st.header("Ranking de População por Municípios")
n = st.slider(label="selecione a quantidade de municípios", min_value=1,max_value=50)
top_n = requests.get(f"{base_url}/populacao/top-municipios?limit={n}").json()
st.dataframe(top_n)
st.bar_chart(data=top_n, x="nome", y="total", sort=False, horizontal=True)
st.divider()

# ====================
# População por Região
# ====================
st.header("População por Região")
populacao_regiao = requests.get(f"{base_url}/populacao/por-regiao").json()
pop_regiao_df = pd.DataFrame(populacao_regiao)
fig, ax = plt.subplots()
ax.pie(data=pop_regiao_df, x="total", labels="nome", startangle=90, autopct="%1.1f%%")
ax.axis("equal")
_,c,_ = st.columns([0.5,1.5,0.5])
with c:
    st.pyplot(fig, use_container_width=False, )
st.divider()

# ====================
# População por Estado
# ====================
st.header("População por Estado")
filtro_regiao = st.selectbox(label="Filtrar por Região", options=["Todas", "Norte", "Nordeste", "Sul", "Sudeste", "Centro-Oeste"])
regiao_nome_id = {
"Norte": 1, "Nordeste": 2, "Sudeste": 3, "Sul": 4, "Centro-Oeste":5
}
if filtro_regiao == "Todas":
    populacao_estado = requests.get(f"{base_url}/populacao/por-uf").json()
else:
    populacao_estado = requests.get(f"{base_url}/populacao/por-uf?id_regiao={regiao_nome_id.get(filtro_regiao)}").json()
pop_uf_df = pd.DataFrame(populacao_estado)
st.bar_chart(data=pop_uf_df, x="nome", y="total")
st.divider()

# ===========================================
# Distribuição da População de cada município
# ===========================================
st.header("População de cada município")
pop_mun = requests.get(f"{base_url}/populacao/distribuicao").json()
pop_mun_df = pd.DataFrame(pop_mun)
fig2, ax2 = plt.subplots()
ax2.hist(pop_mun_df["total"], bins=20)
ax2.set_xlabel("População")
ax2.set_ylabel("Quantidade de municípios")
_,c,_ = st.columns([0.5,1.5,0.5])
with c:
    st.pyplot(fig2, use_container_width=False, )
st.divider()

# ============================
# Dispersão Municípios por Estado
# ============================
st.header("Dispersão Município x Estado")
dispersao = requests.get(f"{base_url}/populacao/dispersao-uf").json()
dispersao_df = pd.DataFrame(dispersao)
# retirar o distrito federal, outlier
dispersao_df = dispersao_df[dispersao_df["media"]<1000000]
dispersao_df = dispersao_df.set_index("nome")
print(dispersao_df)
fig4, ax4 = plt.subplots()
sns.scatterplot(data=dispersao_df, x="media", y="quant", palette="tab10", hue="id_regiao")
ax4.set_xlabel("Média")
ax4.set_ylabel("Quantidade")
ax4.set_title("Média x Quantidade por Região")
_,a,_ = st.columns([0.5,2.0,0.5])
with a:
    st.pyplot(fig4)
st.divider()

# ============================
# Mapa de calor Região x Porte
# ============================
st.header("Mapa de calor Região x Porte")
regiao_porte = requests.get(f"{base_url}/populacao/heatmap-regiao-porte").json()
regiao_porte_df = pd.DataFrame(regiao_porte)
heatmap_df = regiao_porte_df.set_index("nome_regiao")
print(heatmap_df)
fig3, ax3 = plt.subplots()
sns.heatmap(
    heatmap_df,
    annot=True,       # mostra os valores
    fmt="d",          # valores inteiros
    cmap="Blues",
    ax=ax3
)
_,c,_ = st.columns([0.5,1.5,0.5])
with c:
    st.pyplot(fig3)
st.divider()

# ===============
# CRUD MUNICÍPIOS
# ===============
st.header("Gerenciar Municípios")
@st.dialog("Criar Município")
def modal_criar():
    with st.form("form_criar", clear_on_submit=True):
        nome = st.text_input("Nome do Município *")
        estado = st.text_input("Estado a que o Município pertence *")
        populacao = st.text_input("Populacao do Município *")
        if st.form_submit_button("Criar"):
            response = requests.post(f"{base_url}/municipios", params={"nome":nome,"estado":estado,"populacao_inicial":populacao})
            if response.status_code == 201:
                st.success("Município adicionado com sucesso!")
            else:
                st.error("Erro. Tente Novamente.")

@st.dialog("Atualizar Município")
def modal_atualizar():
    with st.form("form_atualizar", clear_on_submit=True):
        id = st.text_input("ID do Município a ser atualizado *")
        nome = st.text_input("Nome do Município")
        estado = st.text_input("Estado a que o Município pertence")
        populacao = st.text_input("Populacao do Município")
        params = {
            "nome": nome,
            "estado": estado,
            "populacao_inicial": populacao,
        }
        if st.form_submit_button("Atualizar"):
            response = requests.put(f"{base_url}/municipios/{id}", params=params)
            if response.status_code == 200:
                st.success("Município atualizado com sucesso!")
            else:
                st.error("Erro. Tente Novamente.")

@st.dialog("Deletar Município")
def modal_deletar():
    with st.form("form_criar", clear_on_submit=True):
        id_municipio = st.text_input("ID do Município a ser deletado")
        if st.form_submit_button("Deletar"):
            response = requests.delete(f"{base_url}/municipios/{id_municipio}")
            if response.status_code == 200:
                print("Município deletado com sucesso!")
            else:
                print("Erro ao deletar Município.")
_,a,b,c,_ = st.columns(5)
with a:
    if st.button("Adicionar Município", type="primary"):
        modal_criar()
with b:
    if st.button("Atualizar Município", type="primary"):
        modal_atualizar()
with c:
    if st.button("Deletar Município", type="primary"):
        modal_deletar()
st.divider()
# ==============
# CRUD CADASTROS
# ==============
st.header("Gerenciar Cadastros sobre Municípios")

cadastros = None
_,a,_ = st.columns([0.5,2,0.5])
with a:
    with st.form("form_criar", clear_on_submit=True):
        id_municipio = st.text_input("Buscar Registros por ID do município")
        if st.form_submit_button("Buscar"):
            cadastros = requests.get(f"{base_url}/municipios/{id_municipio}/registros").json()
            if cadastros:
                st.dataframe(cadastros)

@st.dialog("Criar Cadastro")
def modal_criar_cadastro():
    with st.form("form_criar", clear_on_submit=True):
        id = st.text_input("ID do Município *")
        obs = st.text_input("Observação sobre o Registro *")
        resp = st.text_input("Responsável pelo Registro *")
        if st.form_submit_button("Criar"):
            response = requests.post(f"{base_url}/municipios/{id}/registros", params={"obs":obs,"responsavel":resp})
            if response.status_code == 201:
                st.success("Registro adicionado com sucesso!")
            else:
                st.error("Erro. Tente Novamente.")

@st.dialog("Atualizar Cadastro")
def modal_atualizar_cadastro():
    with st.form("form_atualizar", clear_on_submit=True):
        id = st.text_input("ID do Registro *")
        obs = st.text_input("Obs do Registro")
        resp = st.text_input("Novo Responsável pelo Registro")
        params = {
            "obs": obs,
            "resp": resp,
        }
        if st.form_submit_button("Atualizar"):
            response = requests.put(f"{base_url}/registros/{id}", params=params)
            if response.status_code == 200:
                st.success("Registro atualizado com sucesso!")
            else:
                st.error("Erro. Tente Novamente.")

@st.dialog("Deletar Cadastro")
def modal_deletar_cadastro():
    with st.form("form_criar", clear_on_submit=True):
        id_registro = st.text_input("ID do Registro a ser deletado")
        if st.form_submit_button("Deletar"):
            response = requests.delete(f"{base_url}/registros/{id_registro}")
            if response.status_code == 200:
                print("Registro deletado com sucesso!")
            else:
                print("Erro ao deletar Município.")
_,a,b,c,_ = st.columns(5)
with a:
    if st.button("Adicionar Cadastro", type="primary"):
        modal_criar_cadastro()
with b:
    if st.button("Atualizar Cadastro", type="primary"):
        modal_atualizar_cadastro()
with c:
    if st.button("Deletar Cadastro", type="primary"):
        modal_deletar_cadastro()

st.divider()



