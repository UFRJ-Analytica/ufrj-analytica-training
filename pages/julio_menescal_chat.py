import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/agent/julio-menescal/chat"


st.set_page_config(
    page_title="Agente Financeiro Educacional",
    page_icon="💰",
)

st.title("💰 Agente Financeiro Educacional")

st.caption(
    "Aprenda conceitos financeiros e realize cálculos "
    "de forma simples e didática."
)

if "messages" not in st.session_state:
    st.session_state.messages = []


# Área da conversa com altura limitada e scroll.
chat_container = st.container(height=500)

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


prompt = st.chat_input("Digite sua dúvida financeira...")

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    try:
        with st.spinner("O agente está analisando sua pergunta..."):
            response = requests.post(
                API_URL,
                json={
                    "message": prompt,
                    "history": st.session_state.messages[:-1],
                },
                timeout=60,
            )

            response.raise_for_status()

        resposta_agente = response.json()["response"]

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": resposta_agente,
            }
        )

        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(resposta_agente)

    except requests.RequestException as exc:
        st.error(
            f"Não foi possível comunicar com o backend: {exc}"
        )

    except (KeyError, ValueError):
        st.error(
            "O backend retornou uma resposta em formato inesperado."
        )