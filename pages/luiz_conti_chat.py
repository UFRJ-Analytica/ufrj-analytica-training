import os

import requests
import streamlit as st

CHAT_ENDPOINT = "http://127.0.0.1:8000/agent/agente_python_luiz_conti/chat"

st.set_page_config(page_title="Agente Python")
st.title("Agente Python")
st.caption("Pergunte qualquer coisa sobre Python e eu irei ajudá-lo")

if "messages" not in st.session_state:
    st.session_state.messages = []


def renderizar_mensagem(role: str, content: str) -> None:
    if role == "user":
        _, coluna = st.columns([2, 8])
        with coluna:
            st.chat_message("user").write(content)
    else:
        coluna, _ = st.columns([8, 2])
        with coluna:
            st.chat_message("assistant").write(content)


def historico_para_backend() -> list[dict[str, str]]:
    return [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]


def chamar_backend(mensagem: str, historico: list[dict[str, str]]) -> str:
    resposta = requests.post(
        CHAT_ENDPOINT,
        json={"message": mensagem, "history": historico},
        timeout=60,
    )
    resposta.raise_for_status()
    return resposta.json()["response"]


chat_area = st.container(height=400)

with chat_area:
    for mensagem in st.session_state.messages:
        renderizar_mensagem(mensagem["role"], mensagem["content"])

entrada = st.chat_input("Digite sua mensagem")

if entrada:
    st.session_state.messages.append({"role": "user", "content": entrada})
    historico = historico_para_backend()[:-1]

    with chat_area:
        renderizar_mensagem("user", entrada)
        with st.spinner("Processando"):
            try:
                resposta = chamar_backend(entrada, historico)
            except requests.exceptions.ConnectionError:
                resposta = "Nao foi possivel conectar ao backend."
            except requests.exceptions.Timeout:
                resposta = "O backend nao respondeu dentro do tempo esperado."
            except Exception as exc:
                resposta = f"Erro ao processar a solicitacao: {exc}"
        renderizar_mensagem("assistant", resposta)

    st.session_state.messages.append({"role": "assistant", "content": resposta})