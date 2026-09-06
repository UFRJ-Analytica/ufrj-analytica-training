import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API = "http://127.0.0.1:8000/arthur-pereira"

st.title("Acompanhamento Populacional")

#KPIs

c1, c2, c3, c4 = st.columns(4)
c1.metric("Municípios", resumo["total_municipios"])
c2.metric("Estados", resumo["total_estados"])
c3.metric("População Total", f"{resumo['populacao_total']:,}".replace(",", "."))
c4.metric(f"Mais Populoso ({resumo['ano_referencia']})", resumo["municipio_mais_populoso"])

st.divider()

#análise e gráficos

st.header("Análise de Dados")

# Top N
n = st.slider("Quantidade no Ranking:", 5, 20, 10)
df_top = pd.DataFrame(requests.get(f"{API}/populacao/top-municipios", params={"limit": n}).json())
st.plotly_chart(px.bar(df_top, x="nome_municipio", y="populacao", title=f"Top {n} Municípios"), use_container_width=True)
st.dataframe(df_top, use_container_width=True)

# Região e Estado
df_reg = pd.DataFrame(requests.get(f"{API}/populacao/por-regiao").json())
st.plotly_chart(px.pie(df_reg, names="nome_regiao", values="populacao_total", title="População por Região"), use_container_width=True)

reg_id = st.selectbox(
    "Filtrar Estado por Região:",
    [None, 1, 2, 3, 4, 5],
    format_func=lambda x: "Todas as Regiões" if x is None else f"Região ID {x}")

params = {"id_regiao": reg_id} if reg_id else {}
df_uf = pd.DataFrame(requests.get(f"{API}/populacao/por-uf", params=params).json())
st.plotly_chart(px.bar(df_uf, x="sigla_uf", y="populacao_total", title="População por Estado"), use_container_width=True)

# Histograma e Dispersão
df_dist = pd.DataFrame(requests.get(f"{API}/populacao/distribuicao").json())
st.plotly_chart(px.histogram(df_dist, x="populacao", log_y=True, title="Distribuição Populacional"), use_container_width=True)

df_disp = pd.DataFrame(requests.get(f"{API}/populacao/dispersao-uf").json())
st.plotly_chart(
    px.scatter(df_disp, x="total_municipios", y="populacao_media", color="nome_regiao", text="sigla_uf", title="Municípios x População Média por Estado"),
    use_container_width=True
)

# Heatmap
df_heat = pd.DataFrame(requests.get(f"{API}/populacao/heatmap-regiao-porte").json()).pivot(
    index="nome_regiao", columns="porte", values="total_municipios"
).fillna(0)
st.plotly_chart(px.imshow(df_heat, text_auto=True, title="Mapa de Calor: Região x Porte"), use_container_width=True)

st.divider()


# gerenciar municípios

st.header("Gerenciar Municípios")

with st.form("criar_muni"):
    st.subheader("Novo Município")
    nome = st.text_input("Nome:")
    id_uf = st.number_input("ID do Estado (ex: 33 RJ, 35 SP):", value=33, step=1)
    pop = st.number_input("População:", value=10000, step=1000)
    if st.form_submit_button("Cadastrar Município"):
        requests.post(f"{API}/municipios", json={"nome_municipio": nome, "id_uf": int(id_uf), "populacao": int(pop)})
        st.success("Município cadastrado!")

id_muni = st.number_input("ID do Município para editar/remover:", min_value=1, step=1)
novo_nome = st.text_input("Novo Nome:")
col_b1, col_b2 = st.columns(2)
if col_b1.button("Atualizar Nome"):
    requests.put(f"{API}/municipios/{id_muni}", json={"nome_municipio": novo_nome})
    st.success("Atualizado!")
if col_b2.button("Excluir Município"):
    requests.delete(f"{API}/municipios/{id_muni}")
    st.success("Excluído!")

st.divider()


# 4. anotações do gestor

st.header("Anotações do Gestor")

id_gestor = st.number_input("ID do Município para anotação:", min_value=1, step=1, key="id_gestor")

with st.form("nova_anotacao"):
    st.subheader("Nova Anotação")
    status = st.selectbox("Status", ["Em Acompanhamento", "Prioritário", "Resolvido", "Pendente"])
    prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Urgente"])
    obs = st.text_input("Observação:")
    resp = st.text_input("Responsável:")
    if st.form_submit_button("Salvar Anotação"):
        requests.post(
            f"{API}/municipios/{id_gestor}/registros",
            json={"status": status, "prioridade": prioridade, "observacao": obs, "responsavel": resp}
        )
        st.success("Anotação criada!")

st.subheader("Anotações Salvas")
registros = requests.get(f"{API}/municipios/{id_gestor}/registros").json()
if registros:
    st.dataframe(pd.DataFrame(registros), use_container_width=True)
    id_del_reg = st.number_input("ID da Anotação para excluir:", min_value=1, step=1)
    if st.button("Excluir Anotação"):
        requests.delete(f"{API}/registros/{id_del_reg}")
        st.success("Anotação removida!")
        st.rerun()
else:
    st.info("Nenhuma anotação cadastrada para este ID.")