import re
import requests
import streamlit as st

st.set_page_config(
    page_title="Chat Académico",
    page_icon="🎓",
    layout="centered"
)

BACKEND_URL = "http://127.0.0.1:8000/agent/caroline-nomura/chat"

st.markdown(
    """
    <style>
    /* Área de rolagem com altura máxima */
    .chat-scroll-container {
        height: 520px;
        overflow-y: auto;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background-color: #f8fafc;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    /* Mensagem do Utilizador (Alinhada à direita) */
    .chat-bubble-user {
        align-self: flex-end;
        background-color: #1e3a8a;
        color: #ffffff;
        padding: 0.75rem 1.1rem;
        border-radius: 14px 14px 2px 14px;
        max-width: 75%;
        word-wrap: break-word;
        font-size: 0.95rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Mensagem do Agente (Alinhada à esquerda) */
    .chat-bubble-assistant {
        align-self: flex-start;
        background-color: #ffffff;
        color: #1e293b;
        padding: 0.85rem 1.2rem;
        border-radius: 14px 14px 14px 2px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 0.95rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        line-height: 1.5;
    }

    .chat-bubble-assistant p {
        margin-bottom: 0.5rem;
    }
    .chat-bubble-assistant h3, .chat-bubble-assistant h4 {
        margin-top: 0.6rem;
        margin-bottom: 0.4rem;
        color: #0f172a;
    }
    .chat-bubble-assistant ul, .chat-bubble-assistant ol {
        margin-left: 1.2rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Assistente de Pesquisa para TCCs")
st.markdown(
    """
    <p style="font-size: 1.05rem; color: #4a5568; margin-top: -0.5rem; margin-bottom: 1.2rem; line-height: 1.4;">
        Estou aqui para te auxiliar a estruturar o teu TCC, encontrar boas referências em fontes de acesso aberto e definir títulos claros. Como posso ajudar hoje?
    </p>
    """,
    unsafe_allow_html=True
)

def renderizar_markdown(texto: str) -> str:
    texto = re.sub(r"^### (.*?)$", r"<h4>\1</h4>", texto, flags=re.MULTILINE)
    texto = re.sub(r"^## (.*?)$", r"<h3>\1</h3>", texto, flags=re.MULTILINE)
    texto = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"\*(.*?)\*", r"<em>\1</em>", texto)
    texto = texto.replace("\n", "<br>")
    return texto

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Olá! Sou a tua assistente de pesquisa académica. Podes colocar dúvidas sobre formatos de título, fontes ou estrutura de secções para o teu TCC."
        }
    ]

# Renderização do histórico
container_html = '<div class="chat-scroll-container">'
for msg in st.session_state.messages:
    if msg["role"] == "user":
        content = msg["content"].replace("\n", "<br>")
        container_html += f'<div class="chat-bubble-user">{content}</div>'
    else:
        content = renderizar_markdown(msg["content"])
        container_html += f'<div class="chat-bubble-assistant">{content}</div>'
container_html += '</div>'

st.markdown(container_html, unsafe_allow_html=True)

def enviar_mensagem(texto_usuario: str):
    texto = texto_usuario.strip()
    if not texto:
        return

    st.session_state.messages.append({"role": "user", "content": texto})

    payload = {
        "message": texto,
        "history": [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]
    }

    with st.spinner("O agente está a analisar a pergunta..."):
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                bot_reply = data.get("response", "Não foi possível obter uma resposta do agente.")
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                st.error(f"Erro no servidor ({response.status_code}): {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Falha ao comunicar com o backend. Certifique-se de que o FastAPI está ativo na porta 8000.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {str(e)}")

    st.rerun()

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            label="Digite a mensagem",
            placeholder="Ex: Como estruturar a introdução de um TCC em computação?",
            label_visibility="collapsed"
        )
    with col2:
        submitted = st.form_submit_button("Enviar", use_container_width=True)

if submitted and user_input:
    enviar_mensagem(user_input)