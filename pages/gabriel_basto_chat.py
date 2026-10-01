import os

import requests
import streamlit as st

st.set_page_config(page_title="Agente de Filmes — Gabriel Basto", page_icon="🎬")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8010")
ENDPOINT = f"{BACKEND_URL}/agent/filmes/chat"

st.title("🎬 Agente de Filmes")
st.caption("Converse com o agente para descobrir, comparar e entender filmes.")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

st.markdown(
    """
    <style>
    .msg-usuario {
        background-color: #0078D7; /* Cor de fundo do usuário (Ex: Azul) */
        color: #FFFFFF;            /* Cor do texto do usuário */
        padding: 10px 14px;
        border-radius: 12px;
        margin: 6px 0;
        max-width: 75%;
        margin-left: auto;
        text-align: right;
    }
    .msg-agente {
        background-color: #673AB7; /* Cor de fundo do agente (Ex: Roxo) */
        color: #FFFFFF;            /* Cor do texto do agente */
        padding: 10px 14px;
        border-radius: 12px;
        margin: 6px 0;
        max-width: 75%;
        margin-right: auto;
        text-align: left;
    }
    .icone-robo {
        font-family: "Segoe UI Emoji", "Apple Color Emoji", sans-serif;
        font-size: 1.4em; /* Aumenta o tamanho do robô */
        vertical-align: middle;
        margin-right: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


historico = st.container(height=420)

with historico:
    for msg in st.session_state.mensagens:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-usuario">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-agente"><span class="icone-robo">🤖</span> {msg["content"]}</div>', unsafe_allow_html=True)


pergunta = st.chat_input("Pergunte algo sobre filmes...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})

    with historico:
        st.markdown(f'<div class="msg-usuario">{pergunta}</div>', unsafe_allow_html=True)

        with st.spinner("O agente está pensando..."):
            try:
                resposta_http = requests.post(ENDPOINT, json={"message": pergunta}, timeout=60)
                resposta_http.raise_for_status()
                resposta_texto = resposta_http.json()["response"]
            except requests.exceptions.ConnectionError:
                resposta_texto = (
                    "⚠️ Não foi possível conectar ao backend. Verifique se a API "
                    "FastAPI está em execução."
                )
            except requests.exceptions.Timeout:
                resposta_texto = "⚠️ O backend demorou demais para responder. Tente novamente."
            except Exception as exc:  
                resposta_texto = f"⚠️ Ocorreu um erro inesperado: {exc}"

        st.markdown(f'<div class="msg-agente"><span class="icone-robo">🤖</span> {resposta_texto}</div>', unsafe_allow_html=True)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta_texto})
