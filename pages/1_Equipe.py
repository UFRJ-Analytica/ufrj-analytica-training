from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "membros.csv"


@st.cache_data
def load_membros() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


st.set_page_config(page_title="Equipe | Analytica Training", page_icon=":busts_in_silhouette:", layout="wide")

df = load_membros()

st.title("Equipe")
st.caption("Visao basica dos membros do programa.")

filtro1, filtro2 = st.columns(2)
trilhas = ["Todas"] + sorted(df["trilha"].dropna().unique().tolist())
areas = ["Todas"] + sorted(df["area"].dropna().unique().tolist())

trilha = filtro1.selectbox("Filtrar por trilha", trilhas)
area = filtro2.selectbox("Filtrar por area", areas)

filtrado = df.copy()
if trilha != "Todas":
    filtrado = filtrado[filtrado["trilha"] == trilha]
if area != "Todas":
    filtrado = filtrado[filtrado["area"] == area]

col1, col2, col3 = st.columns(3)
col1.metric("Pessoas exibidas", int(len(filtrado)))
col2.metric("Carga media", f"{filtrado['disponibilidade_horas'].mean():.1f} h/sem")
col3.metric("Trilhas ativas", int(filtrado["trilha"].nunique()))

st.dataframe(
    filtrado,
    use_container_width=True,
    hide_index=True,
)

st.subheader("Cards da equipe")
for start in range(0, len(filtrado), 2):
    cols = st.columns(2)
    for idx, (_, membro) in enumerate(filtrado.iloc[start : start + 2].iterrows()):
        with cols[idx]:
            st.markdown(
                f"""
                #### {membro["nome"]}
                **Area:** {membro["area"]}  
                **Trilha:** {membro["trilha"]}  
                **Disponibilidade:** {membro["disponibilidade_horas"]} h/sem  
                **Contato:** {membro["email"]}  

                {membro["bio"]}
                """
            )
