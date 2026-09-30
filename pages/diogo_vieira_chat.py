import os

import requests
import streamlit as st

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CHAT_URL = f"{BASE_URL}/agent/diogo-vieira/chat"
TIMEOUT_SEGUNDOS = 60

# chave própria para não misturar com o session_state de outras páginas
CHAVE_HISTORICO = "diogo_games_chat_messages"

st.title("🎮 Game Advisor")
st.caption("Agente de games: pergunte sobre jogos, gêneros e plataformas.")

if CHAVE_HISTORICO not in st.session_state:
    st.session_state[CHAVE_HISTORICO] = []

if st.sidebar.button("🗑️ Limpar conversa"):
    st.session_state[CHAVE_HISTORICO] = []
    st.rerun()


def exibir_mensagem(mensagem: dict) -> None:
    """Agente à esquerda, usuário à direita."""
    if mensagem["role"] == "user":
        _, direita = st.columns([1, 3])
        with direita:
            with st.chat_message("user"):
                st.markdown(mensagem["content"])
    else:
        esquerda, _ = st.columns([3, 1])
        with esquerda:
            with st.chat_message("assistant"):
                st.markdown(mensagem["content"])


def chamar_agente(mensagem: str, historico: list[dict]) -> str:
    payload = {
        "message": mensagem,
        "history": [{"role": m["role"], "content": m["content"]} for m in historico],
    }
    resposta = requests.post(CHAT_URL, json=payload, timeout=TIMEOUT_SEGUNDOS)

    if resposta.status_code != 200:
        try:
            detalhe = resposta.json().get("detail", resposta.text)
        except ValueError:
            detalhe = resposta.text
        raise RuntimeError(f"O backend respondeu com erro {resposta.status_code}: {detalhe}")

    return resposta.json()["response"]


# Área de mensagens: altura limitada e com scroll
area_mensagens = st.container(height=520, border=True)

with area_mensagens:
    if not st.session_state[CHAVE_HISTORICO]:
        st.info("Comece perguntando, por exemplo: *Me recomende um RPG para Nintendo Switch.*")
    for mensagem in st.session_state[CHAVE_HISTORICO]:
        exibir_mensagem(mensagem)

# Campo de texto fixo na parte inferior (o botão de envio é a seta do próprio campo)
pergunta = st.chat_input("Pergunte sobre jogos...")

if pergunta:
    historico_anterior = list(st.session_state[CHAVE_HISTORICO])
    mensagem_usuario = {"role": "user", "content": pergunta}
    st.session_state[CHAVE_HISTORICO].append(mensagem_usuario)

    with area_mensagens:
        exibir_mensagem(mensagem_usuario)
        try:
            with st.spinner("O agente está pensando..."):
                texto = chamar_agente(pergunta, historico_anterior)
        except requests.exceptions.ConnectionError:
            st.error(
                f"Não foi possível conectar ao backend em {BASE_URL}. "
                "Verifique se a API está rodando."
            )
        except requests.exceptions.Timeout:
            st.error("O backend demorou demais para responder. Tente novamente.")
        except RuntimeError as exc:
            st.error(str(exc))
        else:
            mensagem_agente = {"role": "assistant", "content": texto}
            st.session_state[CHAVE_HISTORICO].append(mensagem_agente)
            exibir_mensagem(mensagem_agente)