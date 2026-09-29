"""Interface de conversa com o agente tutor."""

import html
import os

import requests
import streamlit as st


API_URL = os.getenv(
    "LUIZ_CONTI_AGENT_URL",
    "http://127.0.0.1:8000/agent/luiz-conti/chat",
)
STATE_KEY = "luiz_conti_chat"

st.set_page_config(page_title="Tutor de dados", page_icon=":speech_balloon:", layout="centered")
st.title("Tutor de análise de dados")
st.caption("Faça perguntas sobre Python, SQL e análise populacional.")

if STATE_KEY not in st.session_state:
    st.session_state[STATE_KEY] = [
        {"role": "assistant", "content": "Olá! Qual conceito de dados você quer estudar?"}
    ]

for message in st.session_state[STATE_KEY]:
    with st.chat_message(message["role"]):
        st.markdown(html.escape(message["content"]))

if prompt := st.chat_input("Digite uma dúvida"):
    previous = list(st.session_state[STATE_KEY])
    st.session_state[STATE_KEY].append({"role": "user", "content": prompt})
    try:
        response = requests.post(
            API_URL,
            json={"message": prompt, "history": previous},
            timeout=60,
        )
        response.raise_for_status()
        answer = response.json()["response"]
    except requests.RequestException as exc:
        answer = f"Não foi possível consultar o agente: {exc}"
    st.session_state[STATE_KEY].append({"role": "assistant", "content": answer})
    st.rerun()

if st.sidebar.button("Limpar conversa", use_container_width=True):
    del st.session_state[STATE_KEY]
    st.rerun()
