import os

import requests
import streamlit as st

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000") + "/agent/agente-financeiro/chat"

st.set_page_config(page_title="Agente Financeiro")

# joga as mensagens do usuário para a direita
st.markdown(
    """
    <style>
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Agente Financeiro Educacional")
st.caption("Tire dúvidas sobre juros, inflação e renda fixa, ou peça para ele fazer as contas.")

# chave com prefixo porque o session_state é compartilhado entre as páginas
if "sylvio_historico" not in st.session_state:
    st.session_state.sylvio_historico = []

historico = st.session_state.sylvio_historico


def perguntar(mensagem: str, historico: list[dict]) -> str:
    r = requests.post(API_URL, json={"message": mensagem, "history": historico}, timeout=90)
    r.raise_for_status()
    return r.json()["response"]


area = st.container(height=450)

with area:
    for msg in historico:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    with area:
        with st.chat_message("user"):
            st.markdown(pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    resposta = perguntar(pergunta, historico)
                except requests.ConnectionError:
                    st.error("Não consegui conectar ao backend. Confira se o uvicorn está rodando.")
                    st.stop()
                except requests.HTTPError as exc:
                    st.error(f"Erro no agente: {exc.response.json().get('detail', exc)}")
                    st.stop()
                except requests.RequestException as exc:
                    st.error(f"O backend respondeu com erro: {exc}")
                    st.stop()
            st.markdown(resposta)

    historico.append({"role": "user", "content": pergunta})
    historico.append({"role": "assistant", "content": resposta})