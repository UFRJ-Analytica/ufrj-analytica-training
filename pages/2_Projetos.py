from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "projetos.csv"


@st.cache_data
def load_projetos() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


st.set_page_config(page_title="Projetos | Analytica Training", page_icon=":clipboard:", layout="wide")

df = load_projetos()

st.title("Projetos")
st.caption("Acompanhamento inicial das frentes do treinamento.")

col1, col2 = st.columns(2)
status_opcoes = ["Todos"] + sorted(df["status"].dropna().unique().tolist())
frente_opcoes = ["Todas"] + sorted(df["frente"].dropna().unique().tolist())

status = col1.selectbox("Filtrar por status", status_opcoes)
frente = col2.selectbox("Filtrar por frente", frente_opcoes)

filtrado = df.copy()
if status != "Todos":
    filtrado = filtrado[filtrado["status"] == status]
if frente != "Todas":
    filtrado = filtrado[filtrado["frente"] == frente]

k1, k2, k3 = st.columns(3)
k1.metric("Projetos exibidos", int(len(filtrado)))
k2.metric("Progresso medio", f"{filtrado['progresso'].mean():.0f}%")
k3.metric("Responsaveis", int(filtrado["responsavel"].nunique()))

st.dataframe(filtrado, use_container_width=True, hide_index=True)

st.subheader("Resumo visual")
for _, projeto in filtrado.iterrows():
    with st.container(border=True):
        top1, top2, top3 = st.columns((2, 1, 1))
        top1.markdown(f"### {projeto['projeto']}")
        top2.markdown(f"**Status:** {projeto['status']}")
        top3.markdown(f"**Prioridade:** {projeto['prioridade']}")
        st.write(projeto["descricao"])
        meta1, meta2 = st.columns(2)
        meta1.markdown(f"**Frente:** {projeto['frente']}")
        meta2.markdown(f"**Responsavel:** {projeto['responsavel']}")
        st.progress(int(projeto["progresso"]) / 100)
