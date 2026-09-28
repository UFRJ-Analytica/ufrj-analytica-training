import streamlit as st
import requests


if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("MyNutri")


with st.container(height=500):
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


mensagem = st.chat_input("Digite sua mensagem...")


if mensagem:
    st.session_state.messages.append({
        "role": "user",
        "content": mensagem
    })

    with st.chat_message("user"):
        st.write(mensagem)

    try:
        with st.spinner("MyNutri está pensando..."):
            response = requests.post(
                "http://localhost:8000/agent/mynutri/chat",
                json={"message": mensagem}
            )

        if response.status_code == 200:
            resposta = response.json()["response"]

            st.session_state.messages.append({
                "role": "assistant",
                "content": resposta
            })

            with st.chat_message("assistant"):
                st.write(resposta)

        else:
            st.error(
                f"Erro ao enviar mensagem: {response.status_code}\n\n"
                f"{response.text}"
            )

    except requests.exceptions.RequestException as e:
        st.error(
            f"Não foi possível conectar ao servidor: {e}"
        )