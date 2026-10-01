import os

import requests
import streamlit as st

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
API_URL = f"{BASE_URL}/agent/luiz-paulo/chat"
CHAVE_HISTORICO = "luiz_paulo_chat_messages"
ALTURA_CONVERSA = 460
TIMEOUT_SEGUNDOS = 120
MAX_CARACTERES_ERRO = 220

st.set_page_config(page_title="Agente de Pesquisa Acadêmica")

st.title("Agente de Pesquisa Acadêmica")
st.caption(
    "Pergunte sobre artigos de ciência de dados."
)

if CHAVE_HISTORICO not in st.session_state:
    st.session_state[CHAVE_HISTORICO] = [
        {
            "role": "assistant",
            "content": (
                "Olá! Posso procurar artigos na minha coleção de ciência de dados. "
            ),
        }
    ]


def chamar_agente(mensagem: str, historico: list[dict]) -> str:
    """conversa com o backend FastAPI"""
    resposta = requests.post(
        API_URL,
        json={"message": mensagem, "history": historico},
        timeout=TIMEOUT_SEGUNDOS,
    )
    resposta.raise_for_status()
    return resposta.json()["response"]


def detalhe_do_erro(erro: requests.exceptions.HTTPError) -> str:
    """A API devolve o motivo do erro casotenha.
    """
    try:
        detalhe = erro.response.json().get("detail", str(erro))
    except ValueError:
        detalhe = str(erro)
    return detalhe[:MAX_CARACTERES_ERRO].rstrip() + ("..." if len(detalhe) > MAX_CARACTERES_ERRO else "")


def renderizar_mensagem(mensagem: dict) -> None:
    if mensagem["role"] == "user":
        _, coluna = st.columns([1, 2])
    else:
        coluna, _ = st.columns([2, 1])

    with coluna, st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])


with st.sidebar:
    st.subheader("Conversa")
    st.write(f"Backend: `{API_URL}`")
    if st.button("Limpar conversa", use_container_width=True):
        del st.session_state[CHAVE_HISTORICO]
        st.rerun()

# Altura fixa: dá scroll e impede a página de crescer sem limite.
area_conversa = st.container(height=ALTURA_CONVERSA)
with area_conversa:
    for mensagem in st.session_state[CHAVE_HISTORICO]:
        renderizar_mensagem(mensagem)

pergunta = st.chat_input("Pergunte sobre um tema de pesquisa...")

if pergunta:
    # O histórico enviado é o anterior à pergunta, senão ela iria duplicada.
    historico_anterior = list(st.session_state[CHAVE_HISTORICO])
    st.session_state[CHAVE_HISTORICO].append({"role": "user", "content": pergunta})

    with st.spinner("Consultando o agente..."):
        try:
            resposta = chamar_agente(pergunta, historico_anterior)
        except requests.exceptions.ConnectionError:
            resposta = (
                "não consegui falar com o backend. Confira se a API está no ar "
                f"em `{BASE_URL}`."
            )
        except requests.exceptions.Timeout:
            resposta = "O agente demorou demais para responder. Tente de novo."
        except requests.exceptions.HTTPError as erro:
            resposta = f"O backend recusou a requisição: {detalhe_do_erro(erro)}"
        except requests.exceptions.RequestException as erro:
            resposta = f"Erro ao chamar o backend: {erro}"

    st.session_state[CHAVE_HISTORICO].append({"role": "assistant", "content": resposta})
    st.rerun()
