import streamlit as st
import requests

st.set_page_config(page_title="Agente Eduardo Borges", page_icon="🤖")

st.title("🤖 Chat com Agente Eduardo Borges")
st.write("Agente de Análise de Dados integrado via FastAPI e LangGraph")

# Endpoint local do FastAPI
API_URL = "http://127.0.0.1:8000/agent/eduardo-borges/chat"

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto do chat
if prompt := st.chat_input("Pergunte algo ao agente..."):
    # Desenha a mensagem do usuário
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Chamada para o backend FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            try:
                res = requests.post(
                    API_URL,
                    json={"message": prompt},
                    timeout=30
                )
                if res.status_code == 200:
                    answer = res.json().get("response", "Sem resposta.")
                else:
                    answer = f"Erro na API ({res.status_code}): {res.text}"
            except Exception as e:
                answer = f"Erro de conexão com o backend: {e}"
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})