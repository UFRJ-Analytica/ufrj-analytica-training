from __future__ import annotations

import html
import os
from typing import Any

import requests
import streamlit as st


DEFAULT_BACKEND_URL = os.getenv("SGCONT_API_URL", "http://127.0.0.1:8000/agent/sgcont/chat")
STATE_KEY = "sgcont_chat_messages"

st.set_page_config(
    page_title="SGCont Agent Chat",
    page_icon=":speech_balloon:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-bottom: 6rem; max-width: 980px; }
    .chat-scroll {
        height: 58vh;
        overflow-y: auto;
        border: 1px solid #d9e2ec;
        border-radius: 8px;
        padding: 1rem;
        background: #f8fafc;
    }
    .message-row { display: flex; margin: 0.55rem 0; width: 100%; }
    .message-row.user { justify-content: flex-end; }
    .message-row.assistant { justify-content: flex-start; }
    .bubble {
        max-width: min(74%, 680px);
        padding: 0.8rem 0.95rem;
        border-radius: 8px;
        line-height: 1.45;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
    }
    .bubble.user { background: #174ea6; color: white; border-bottom-right-radius: 3px; }
    .bubble.assistant {
        background: white;
        color: #172033;
        border: 1px solid #e2e8f0;
        border-bottom-left-radius: 3px;
    }
    .sender {
        display: block;
        font-size: 0.74rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
        opacity: 0.8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def inicializar_historico() -> None:
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = [
            {
                "role": "assistant",
                "content": "Ola! Sou o agente SGCont para ajudar nos entregaveis 1 e 2.",
            }
        ]


def renderizar_historico(messages: list[dict[str, str]]) -> None:
    linhas = ['<div class="chat-scroll">']

    for item in messages:
        role = item.get("role", "assistant")
        css_role = "user" if role == "user" else "assistant"
        remetente = "Voce" if css_role == "user" else "Agente"
        conteudo = html.escape(item.get("content", ""))

        linhas.append(
            f'<div class="message-row {css_role}">' f'<div class="bubble {css_role}">'
            f'<span class="sender">{remetente}</span>' f"{conteudo}" "</div>" "</div>"
        )

    linhas.append("</div>")
    st.markdown("".join(linhas), unsafe_allow_html=True)


def chamar_backend(backend_url: str, message: str, history: list[dict[str, str]]) -> str:
    payload: dict[str, Any] = {"message": message, "history": history}
    response = requests.post(backend_url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return str(data.get("response", "Resposta sem conteudo."))


inicializar_historico()

st.title("Agente SGCont")
st.caption("Chat Streamlit integrado ao backend FastAPI e ao agente em LangGraph.")

with st.sidebar:
    st.subheader("Backend")
    backend_url = st.text_input("Endpoint do agente", value=DEFAULT_BACKEND_URL)
    if st.button("Limpar conversa", use_container_width=True):
        del st.session_state[STATE_KEY]
        st.rerun()

renderizar_historico(st.session_state[STATE_KEY])

prompt = st.chat_input("Digite sua mensagem para o agente")

if prompt:
    historico_anterior = list(st.session_state[STATE_KEY])
    st.session_state[STATE_KEY].append({"role": "user", "content": prompt})

    with st.spinner("Agente processando..."):
        try:
            resposta = chamar_backend(backend_url, prompt, historico_anterior)
        except requests.exceptions.ConnectionError:
            resposta = (
                "Nao consegui conectar ao backend. Verifique se o FastAPI esta rodando em "
                "http://127.0.0.1:8000."
            )
        except requests.exceptions.Timeout:
            resposta = "O backend demorou demais para responder. Tente novamente."
        except requests.exceptions.HTTPError as exc:
            resposta = f"O backend retornou erro HTTP: {exc.response.status_code}."
        except requests.exceptions.RequestException as exc:
            resposta = f"Erro ao chamar o backend: {exc}"

    st.session_state[STATE_KEY].append({"role": "assistant", "content": resposta})
    st.rerun()
