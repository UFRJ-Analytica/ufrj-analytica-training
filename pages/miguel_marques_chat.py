import html                                                        
import os

import requests
import streamlit as st

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ENDPOINT = f"{BASE_URL}/agent/miguel-marques-agent/chat"

st.title("Agente Docker")
st.caption("Tire dúvidas sobre Docker, Dockerfile e Docker Compose.")


st.markdown(
    """
    <style>
    .linha-user { display: flex; justify-content: flex-end; margin: 6px 0; }
    .balao-user {
        max-width: 75%; background: #1f6feb; color: #ffffff;
        padding: 10px 14px; border-radius: 14px 14px 4px 14px; line-height: 1.45;
    }
    div[class*="st-key-bot_"] {
        max-width: 75%; background: rgba(128, 128, 128, 0.15);
        padding: 10px 14px; border-radius: 14px 14px 14px 4px; margin: 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "assistant", "content": "Olá! Sou o Agente Docker. Como posso ajudar?"}
    ]


def chamar_agente(texto: str) -> str:
    """Envia a pergunta ao backend e devolve o texto da resposta (ou uma mensagem de erro)."""
    try:
        r = requests.post(ENDPOINT, json={"message": texto}, timeout=120)
        r.raise_for_status()
        return r.json()["response"]
    except requests.exceptions.ConnectionError:
        return f"⚠️ Não consegui conectar ao backend em {BASE_URL}. Ele está rodando?"
    except requests.exceptions.Timeout:
        return "⚠️ O agente demorou demais para responder. Tente novamente."
    except requests.exceptions.HTTPError as erro:
        try:
            detalhe = erro.response.json().get("detail", "")
        except ValueError:
            detalhe = ""
        return f"⚠️ Erro do backend ({erro.response.status_code}). {detalhe}"


def desenhar(indice: int, role: str, conteudo: str) -> None:       # NOVO
    """Desenha uma mensagem: usuário à direita, agente à esquerda."""
    if role == "user":
        seguro = html.escape(conteudo).replace("\n", "<br>")       # escapa HTML por segurança
        st.markdown(
            f'<div class="linha-user"><div class="balao-user">{seguro}</div></div>',
            unsafe_allow_html=True,
        )
    else:

        with st.container(key=f"bot_{indice}"):
            st.markdown(conteudo)


caixa = st.container(height=500)

with caixa:
    for i, m in enumerate(st.session_state.mensagens):
        desenhar(i, m["role"], m["content"])

pergunta = st.chat_input("Digite sua mensagem...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with caixa:
        desenhar(len(st.session_state.mensagens) - 1, "user", pergunta)
        with st.spinner("O agente está pensando..."):
            resposta = chamar_agente(pergunta)
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        desenhar(len(st.session_state.mensagens) - 1, "assistant", resposta)