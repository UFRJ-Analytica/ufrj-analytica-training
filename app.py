from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

@st.cache_data
def load_membros() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "membros.csv")


@st.cache_data
def load_projetos() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "projetos.csv")


st.set_page_config(
    page_title="Analytica Training",
    page_icon=":bar_chart:",
    layout="wide",
)


membros = load_membros()
projetos = load_projetos()

st.title("Analytica Training | UFRJ")
st.caption("Base inicial em Streamlit para apresentar equipe, projetos e frente de treino.")

col1, col2, col3 = st.columns(3)
col1.metric("Membros ativos", int(len(membros)))
col2.metric("Projetos mapeados", int(len(projetos)))
col3.metric("Frentes", int(projetos["frente"].nunique()))

st.markdown(
    """
    ### Objetivo
    Este app organiza a base inicial do programa de treinamento da Analytica.
    A estrutura foi pensada para crescer com paginas de acompanhamento,
    entregas, trilhas e indicadores.
    """
)

left, right = st.columns((1.3, 1))

with left:
    st.subheader("O que ja esta pronto")
    st.markdown(
        """
        - Home com visao geral do programa.
        - Pagina de equipe com filtros e indicadores.
        - Pagina de projetos com status, prioridade e progresso.
        - Dados de exemplo em CSV para facilitar iteracao.
        """
    )

with right:
    st.subheader("Proximos passos sugeridos")
    st.markdown(
        """
        1. Conectar os CSVs a uma fonte real.
        2. Adicionar autenticacao e papeis.
        3. Incluir cronograma, trilhas e entregas.
        4. Publicar em Streamlit Community Cloud ou ambiente interno.
        """
    )

st.divider()

st.subheader("Snapshot dos projetos")
st.dataframe(
    projetos[["projeto", "frente", "status", "responsavel", "progresso"]],
    use_container_width=True,
    hide_index=True,
)

st.info("Use o menu lateral para navegar entre Equipe e Projetos.") 

#Print Hello World
print("Hello World")
st.info("Fé no mengo.")
