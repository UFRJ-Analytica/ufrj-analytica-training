import streamlit as st
import requests

# Configuração da página e título
st.set_page_config(page_title="Volt - Agente de Energia", page_icon="⚡")
st.title("⚡ Volt: Análise do Setor Elétrico")
st.markdown("Assistente especializado em precificação, PLD e impacto climático (El Niño) nos reservatórios do SIN.")

# Inicialização do histórico de mensagens na sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o Volt. Como posso ajudar com os dados do mercado de energia hoje?"}
    ]

# Container com limite de altura para garantir o scroll (impede crescimento indefinido)
chat_container = st.container(height=500)

# Renderiza o histórico na tela
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Campo de entrada fixo na parte inferior
if user_input := st.chat_input("Pergunte sobre níveis de reservatórios, PLD ou bandeiras tarifárias..."):
    
    # Exibe a mensagem do usuário imediatamente
    st.session_state.messages.append({"role": "user", "content": user_input})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
    
    # Comunicação com o Backend (Desacoplado)
    with chat_container:
        with st.chat_message("assistant"):
            # Indicador de carregamento
            with st.spinner("Analisando dados do setor elétrico..."):
                try:
                    # Endpoint FastAPI do Entregável 1
                    url = "http://127.0.0.1:8000/agent/vanessa-castro/chat"
                    payload = {"message": user_input}
                    
                    response = requests.post(url, json=payload)
                    response.raise_for_status() # Dispara erro se não for 200 OK
                    
                    # Extrai a resposta do agente
                    agent_response = response.json().get("response", "Erro ao extrair resposta.")
                    st.markdown(agent_response)
                    
                    # Salva no histórico
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})
                    
                except requests.exceptions.ConnectionError:
                    erro_msg = "⚠️ Erro de conexão: O backend FastAPI parece estar desligado. Verifique se o Uvicorn está rodando na porta 8000."
                    st.error(erro_msg)
                    st.session_state.messages.append({"role": "assistant", "content": erro_msg})
                except Exception as e:
                    erro_msg = f"⚠️ Ocorreu um erro no processamento: {e}"
                    st.error(erro_msg)
                    st.session_state.messages.append({"role": "assistant", "content": erro_msg})