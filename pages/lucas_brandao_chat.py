import streamlit as st
import requests

#Configuração da página
st.set_page_config(page_title="Planejador Copa 2030")
st.title("Planejador de Viagens - Copa 2030")
st.markdown("Assistente focado em logística internacional, roteiros e orçamentos para a Copa (Espanha, Marrocos e Portugal).")

#URL do endpoint 
API_URL = "http://127.0.0.1:8000/agent/lucas-brandao-agent/chat"

#Inicializa o histórico da conversa 
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Pronto para organizar a viagem da Copa com seus amigos? Como posso ajudar com o roteiro ou orçamento hoje?"}
    ]

#Exibe as mensagens do histórico na tela
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#Caixa de texto na parte inferior pro usuário digitar
if prompt := st.chat_input("Digite sua solicitação (ex: Sugira uma rota começando por Marrocos)"):
    
    #1. Adiciona e mostra a mensagem do usuário na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    #2. Mostra o loading 
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("Analisando roteiros e orçamentos..."):
            try:
                #Prepara os dados para enviar via HTTP para o FastAPI
                payload = {
                    "message": prompt,
                    "history": st.session_state.messages[:-1] 
                }
                
                #Faz o request para o backend
                response = requests.post(API_URL, json=payload)
                response.raise_for_status() 
                
                dados_retorno = response.json()
                conteudo_resposta = dados_retorno.get("response", "")
                
                if isinstance(conteudo_resposta, list):
                    resposta_agente = "".join([
                        bloco.get("text", "") if isinstance(bloco, dict) else str(bloco) 
                        for bloco in conteudo_resposta
                    ])
                else:
                    resposta_agente = str(conteudo_resposta)

                # Mostra a resposta na tela e salva no histórico
                message_placeholder.markdown(resposta_agente)
                st.session_state.messages.append({"role": "assistant", "content": resposta_agente})
                
            except requests.exceptions.ConnectionError:
                st.error("Erro de conexão: O backend (FastAPI) não está rodando. Ligue o servidor primeiro!")
            except Exception as e:
                st.error(f"Ocorreu um erro no processamento: {e}")