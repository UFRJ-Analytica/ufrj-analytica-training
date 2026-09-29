import requests
import streamlit as st

st.set_page_config(
    page_title="Agente de Análise de Dados",
)

st.title("Agente de Análise de Dados")
st.write("Converse com o agente para tirar dúvidas sobre análise de dados")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Digite sua pergunta...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/agent/mariana-freitas/chat",
                    json={"message": prompt}
                )

                response.raise_for_status()

                answer = response.json()["response"]
                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.exceptions.RequestException:
                st.error("Não foi possível conectar ao agente.")