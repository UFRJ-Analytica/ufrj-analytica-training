from __future__ import annotations
import html
import os
from typing import Any
import requests
import streamlit as st


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000/agent/julio_machado_agent/chat"

STATE_KEY = "agente_dados_messages"


st.set_page_config(
    page_title="Agente de Dados",
    page_icon=":bar_chart:",
    layout="wide",
)


st.markdown(
"""
    <style>
    /* Importando outras fontes do google fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem;
        max-width: 900px;
    }

    /* ── Cabeçalho ── */
    .dados-header {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }

    .dados-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 600;
        color: #f8fafc;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .dados-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 400;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 3px;
        padding: 0.15rem 0.45rem;
        vertical-align: middle;
    }

    .dados-caption {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 300;
        margin-top: 0.1rem;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
    }

    /* ── Área de chat ── */
    .chat-scroll {
        height: 56vh;
        overflow-y: auto;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 1.1rem 1.2rem;
        background: #0b0f19;
        scroll-behavior: smooth;
    }

    .message-row {
        display: flex;
        margin: 0.6rem 0;
        width: 100%;
        align-items: flex-end;
    }

    .message-row.user {
        justify-content: flex-end;
    }

    .message-row.assistant {
        justify-content: flex-start;
    }

    /* ── Balões ── */
    .bubble {
        max-width: min(72%, 640px);
        padding: 0.75rem 1rem;
        border-radius: 6px;
        line-height: 1.5;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
        font-size: 0.875rem;
    }

    .bubble.user {
        background: #1e3a8a;
        color: #f8fafc;
        border-bottom-right-radius: 2px;
        font-family: 'Inter', sans-serif;
    }

    .bubble.assistant {
        background: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        border-bottom-left-radius: 2px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
    }

    .sender {
        display: block;
        font-size: 0.68rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        opacity: 0.75;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #0f172a;
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] .stTextInput input {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }

    section[data-testid="stSidebar"] .stButton button {
        background: #1e3a5f !important;
        border: 1px solid #2d5a8e !important;
        color: #bfdbfe !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        border-radius: 4px;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: #2d5a8e !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Funções auxiliares ────────────────────────────────────────────────────────

def inicializar_historico() -> None:
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = [
            {
                "role": "assistant",
                "content": (
                    "Ola! Sou o Agente de Análise de Dados.\n\n"
                    "Realizo cálculos estatísticos"
                    "(media, mediana, desvio padrão, amplitude e mais).\n"
                    "Também posso responder duvidas sobre análise de dados e Pandas."
                ),
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
            f'<div class="message-row {css_role}">'
            f'<div class="bubble {css_role}">'
            f'<span class="sender">{remetente}</span>'
            f"{conteudo}"
            "</div>"
            "</div>"
        )

    linhas.append("</div>")
    st.markdown("".join(linhas), unsafe_allow_html=True)


def chamar_backend(
    backend_url: str,
    message: str,
    history: list[dict[str, str]],
) -> str:
    payload: dict[str, Any] = {
        "message": message,
        "history": history,
    }
    response = requests.post(backend_url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return str(data.get("response", "Resposta sem conteudo."))


# ── Layout ────────────────────────────────────────────────────────────────────

inicializar_historico()

st.title("Agente de Análise de Dados")

st.subheader("Um agente focado em auxiliar o usuário a analisar e manipular dados")

with st.sidebar:
    st.markdown(
        "**:bar_chart: Analytica Training**\n\nAgente de Analise de Dados"
    )
    st.divider()
    st.subheader("Configuracao")
    backend_url = st.text_input("Endpoint do agente", value=DEFAULT_BACKEND_URL)
    st.divider()
    if st.button("Limpar conversa", use_container_width=True):
        del st.session_state[STATE_KEY]
        st.rerun()

renderizar_historico(st.session_state[STATE_KEY])

prompt = st.chat_input("Ex: calcule as estatisticas para 12, 45, 7, 89, 23")

if prompt:
    historico_anterior = list(st.session_state[STATE_KEY])
    st.session_state[STATE_KEY].append({"role": "user", "content": prompt})

    with st.spinner("Calculando e consultando o agente..."):
        try:
            resposta = chamar_backend(backend_url, prompt, historico_anterior)
        except requests.exceptions.ConnectionError:
            resposta = (
                "Nao consegui conectar ao backend.\n"
                "Verifique se o FastAPI esta rodando em http://127.0.0.1:8000."
            )
        except requests.exceptions.Timeout:
            resposta = "O backend demorou demais para responder. Tente novamente."
        except requests.exceptions.HTTPError as exc:
            resposta = f"O backend retornou erro HTTP {exc.response.status_code}."
        except requests.exceptions.RequestException as exc:
            resposta = f"Erro ao chamar o backend: {exc}"

    st.session_state[STATE_KEY].append({"role": "assistant", "content": resposta})
    st.rerun()
