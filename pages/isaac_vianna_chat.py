"""
Pagina Streamlit do Agente de Python (Isaac Vianna).

So conversa com o backend via HTTP (nao importa nada de backend/ nem
executa o agente diretamente).
"""
from __future__ import annotations

import os

import requests
import streamlit as st

# Mesmo padrao sugerido pela tarefa: uma URL base configuravel por
# variavel de ambiente, com o backend local como default.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CHAT_ENDPOINT = f"{BACKEND_URL}/agent/isaac-vianna-python/chat"

STATE_KEY = "isaac_vianna_chat_messages"


# CSS que inverte a direcao das mensagens do usuario (avatar e texto a
# direita), usando :has() para selecionar apenas as mensagens cujo avatar
# e o do usuario (data-testid confirmado na versao instalada do Streamlit
# via `pip show streamlit`).
st.markdown(
    """
    <style>
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🐍 Agente de Python — Isaac Vianna")

if STATE_KEY not in st.session_state:
    st.session_state[STATE_KEY] = []

historico = st.session_state[STATE_KEY]

# Area de mensagens com altura fixa e scroll proprio.
area_mensagens = st.container(height=500, border=True)

with area_mensagens:
    for mensagem in historico:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

prompt = st.chat_input("Pergunte algo sobre Python...")

if prompt:
    historico.append({"role": "user", "content": prompt})
    with area_mensagens:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("O agente está pensando..."):
                try:
                    resposta = requests.post(
                        CHAT_ENDPOINT, json={"message": prompt}, timeout=120
                    )
                    resposta.raise_for_status()
                except requests.exceptions.ConnectionError:
                    st.error("Backend indisponível. Verifique se o FastAPI está rodando.")
                except requests.exceptions.Timeout:
                    st.error("O backend demorou demais para responder. Tente novamente.")
                except requests.exceptions.HTTPError:
                    detalhe = resposta.json().get("detail", resposta.text)
                    st.error(f"O backend retornou um erro: {detalhe}")
                except requests.exceptions.RequestException as exc:
                    st.error(f"Erro ao chamar o backend: {exc}")
                else:
                    texto_resposta = resposta.json()["response"]
                    st.markdown(texto_resposta)
                    historico.append({"role": "assistant", "content": texto_resposta})
