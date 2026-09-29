import streamlit as st
import requests

st.title("Agente de Filmes")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o teu Agente de Filmes. Deseja uma recomendação de filmes para hoje?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escreva a tua pergunta sobre filmes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("A consultar a base de dados..."):
            try:
                url = "http://127.0.0.1:8000/agent/felipe-indio/chat"
                response = requests.post(url, json={"message": prompt})
                response.raise_for_status()
                
                resposta_agente = response.json().get("response", "Erro: Resposta vazia.")
                
                st.markdown(resposta_agente)
                st.session_state.messages.append({"role": "assistant", "content": resposta_agente})
                
            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao comunicar com o backend. Certifica-te de que o FastAPI está funcionando. Detalhes: {e}")