import os

import requests
import streamlit as st


API_URL = os.getenv(
    "PEDRO_AGENT_API_URL",
    "http://127.0.0.1:8000/agent/pedro-ferrari/chat"
)


st.title("🎮 GAMEni")

st.caption(
    "Assistente para pesquisa e recomendação de jogos"
)


if "gameguide_messages" not in st.session_state:
    st.session_state.gameguide_messages = []

    mensagem_inicial = {
        "role": "assistant",
        "content": (
            "Olá! Sou o GAMEni. "
            "Que tipo de jogo você está procurando?"
        )
    }

    st.session_state.gameguide_messages.append(
        mensagem_inicial
    )


def mostrar_mensagem(role, content):
    if role == "user":
        espaco, mensagem = st.columns(
            [1, 4]
        )

        with mensagem:
            with st.container(border=True):
                st.markdown(content)

    else:
        mensagem, espaco = st.columns(
            [4, 1]
        )

        with mensagem:
            with st.container(border=True):
                st.markdown(content)


with st.container(
    height=500,
    border=True
):
    for mensagem in st.session_state.gameguide_messages:
        mostrar_mensagem(
            mensagem["role"],
            mensagem["content"]
        )


mensagem_usuario = st.chat_input(
    "Digite sua mensagem..."
)


if mensagem_usuario:
    historico = (
        st.session_state.gameguide_messages.copy()
    )

    mensagem = {
        "role": "user",
        "content": mensagem_usuario
    }

    st.session_state.gameguide_messages.append(
        mensagem
    )

    try:
        with st.spinner(
            "GAMEni está pensando..."
        ):
            resposta = requests.post(
                API_URL,
                json={
                    "message": mensagem_usuario,
                    "history": historico
                },
                timeout=60
            )

            resposta.raise_for_status()

            dados = resposta.json()

            mensagem_agente = dados["response"]

    except requests.exceptions.HTTPError:
        if resposta.status_code == 429:
            mensagem_agente = (
                "O limite da API Gemini foi atingido. "
                "Tente novamente mais tarde."
            )

        elif resposta.status_code == 503:
            mensagem_agente = (
                "O Gemini está temporariamente indisponível. "
                "Tente novamente em alguns minutos."
            )

        else:
            mensagem_agente = (
                "O agente encontrou um erro "
                "ao processar a mensagem."
            )

    except requests.exceptions.Timeout:
        mensagem_agente = (
            "A resposta demorou mais que o esperado. "
            "Tente novamente em alguns minutos."
        )        

    except requests.exceptions.ConnectionError:
        mensagem_agente = (
            "Não foi possível conectar ao backend."
        )

    except requests.exceptions.RequestException:
        mensagem_agente = (
            "Erro na comunicação com o backend."
        )

    resposta_agente = {
        "role": "assistant",
        "content": mensagem_agente
    }

    st.session_state.gameguide_messages.append(
        resposta_agente
    )

    st.rerun()