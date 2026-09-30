import streamlit as st
import requests

st.set_page_config(
    page_title="Agente de Indicadores Públicos",
    page_icon="📊",
)

st.title("📊 Agente de Indicadores Públicos")
st.markdown(
    "Assistente para consulta e interpretação de indicadores demográficos."
)

API_URL = "http://127.0.0.1:8000/agent/leticia-pessoa/chat"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Olá! Posso ajudar com consultas sobre municípios, "
                "estados, regiões e indicadores populacionais."
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua pergunta..."):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        with st.spinner("Consultando os dados..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"message": prompt},
                    timeout=60,
                )

                response.raise_for_status()

                dados = response.json()

                resposta_agente = dados.get(
                    "response",
                    "O agente não retornou uma resposta.",
                )

                placeholder.markdown(resposta_agente)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": resposta_agente,
                    }
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Não foi possível conectar ao backend. "
                    "Verifique se o FastAPI está rodando na porta 8000."
                )

            except requests.exceptions.Timeout:
                st.error("A resposta do agente demorou mais do que o esperado.")

            except requests.exceptions.RequestException as erro:
                st.error(f"Erro na comunicação com a API: {erro}")

            except Exception as erro:
                st.error(f"Erro inesperado: {erro}")