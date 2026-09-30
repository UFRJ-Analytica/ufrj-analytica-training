import streamlit as st
import requests # faz chamadas http em python

BACKEND_URL = "http://127.0.0.1:8000/agent/juliana-mello/chat"

st.title("Agente Star Wars .𖥔 ݁ ˖🪐.𖥔 ݁ ˖")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "assistant", "content": ".𖥔 ݁ ˖✶⋆.˚ Olá, jovem Padawan! 🪐 Sou o seu assistente Jedi. O que você deseja saber sobre a galáxia hoje? "}
    ]
    # no streamlit, todo o script roda de novo (do início ao fim)
    # a cada interação!! então, se "mensagens" fosse uma variavel normal, ela seria recriada a cada vez e o histórico da conversa ia se perder a cada mensagem nova
    # "st.ssesion_state" é uma "área de memória" que sobrevive a cada execução do script.
    # "if mensagens not in st.session_state" é só pra inicializar a memória na primeira vez que o script roda, e não sobrescrever ela a cada execução
    
chat_container = st.container(height=450)
# cria caixa com altura fixa que se tiver mais conteúdo do que cabe nela, ganha scroll interno

# pra alinhar o input de texto e o botão de enviar com html/css 
with chat_container:
    for msg in st.session_state.mensagens:
        if msg["role"] == "user":
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;margin:8px 0;">'
                f'<div style="background:#DCF8C6;color:#111;padding:10px 14px;'
                f'border-radius:12px;max-width:70%;">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="display:flex;justify-content:flex-start;margin:8px 0;">'
                f'<div style="background:#F1F0F0;color:#111;padding:10px 14px;'
                f'border-radius:12px;max-width:70%;">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )

pergunta = st.chat_input("Digite sua mensagem...") # componente pronto do streamlit que nasce fixo na parte inferior da página!

if pergunta: # devolve None se o usuário não enviou nada, if só roda quando chegar mensagem nova
    st.session_state.mensagens.append({"role": "user", "content": pergunta}) # add mensagem do usuario no historico antes de chamar backend (p aparecer na tela mesmo esperando pela resposta)

    with st.spinner("Estou pensando..."): # mostra o carregando
        try:
            resposta = requests.post( # faz chamada http pro fastapi, transformando o dicionario de python em json
                BACKEND_URL,
                json={"message": pergunta},
                timeout=30,
            )
            resposta.raise_for_status() # se o servidor devolver um erro http, levanta uma exceção
            texto_resposta = resposta.json()["response"]
            st.session_state.mensagens.append({"role": "assistant", "content": texto_resposta})
        except requests.exceptions.RequestException: # cobre qualquer porblema
            st.session_state.mensagens.append({
                "role": "assistant",
                "content": "Não consego te responder agora, padawan :( Verifique se o servidor FastAPI está rodando.",
            })

    st.rerun() # tela se resenha com o histórico atualizado