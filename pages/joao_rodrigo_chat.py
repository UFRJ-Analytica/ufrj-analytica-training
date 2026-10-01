import streamlit as st
import requests

st.title("Nerd musical 🤓")
st.write(
    "simulador de um amigo desempregado que ouve do pagode ao metal e reclama se você chamar house de trance"
)
st.write(
    "isso **É** um experimento: nunca confie em um algoritmo pra decidir o que você vai ouvir no önibus."
)
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Me recomende uma música pra ouvir estudando Docker"):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Olhando meus discos..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/agent/joao-rodrigo/chat",
                    json={"message": prompt}
                )

                if response.status_code == 200:
                    resposta_texto = response.json().get(
                        "response",
                        "sem resposta do backend"
                    )

                else:
                    resposta_texto = (
                        f"erro do FastAPI código {response.status_code}: "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:
                resposta_texto = "verifique se a FastAPI esta no ar"

            st.markdown(resposta_texto)

    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta_texto
    })