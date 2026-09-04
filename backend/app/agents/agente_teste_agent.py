from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND_ENV_FILE)
except ImportError:
    pass

try:
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.graph import END, START, StateGraph
    from langgraph.graph.message import add_messages

    LANGGRAPH_AVAILABLE = True
    LANGGRAPH_IMPORT_ERROR = None
except ImportError as exc:
    LANGGRAPH_AVAILABLE = False
    LANGGRAPH_IMPORT_ERROR = str(exc)


SYSTEM_PROMPT = """
Voce e o Agente Mentor Analytica.

Responsabilidade:
- ajudar trainees a entenderem os entregaveis de orquestracao de IA;
- explicar FastAPI, Streamlit, LangGraph e boas praticas em exemplos pequenos;
- responder em portugues, com tom didatico e objetivo;
- quando a pergunta envolver implementacao, sugerir proximos passos concretos.

Regras:
- nao invente requisitos fora do escopo do treinamento;
- se faltar contexto, diga o que precisa ser validado;
- destaque diferencas entre backend, frontend e agente quando isso ajudar.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("AGENTE_TESTE_MODEL", "gemini-2.5-flash"),
    "temperature": float(os.getenv("AGENTE_TESTE_TEMPERATURE", "0.2")),
    "max_output_tokens": int(os.getenv("AGENTE_TESTE_MAX_OUTPUT_TOKENS", "1024")),
}


def _classificar_texto(mensagem: str) -> dict[str, str]:
    texto = mensagem.lower()

    if any(
        palavra in texto
        for palavra in ["entregavel 2", "streamlit", "front", "frontend", "tela", "chat"]
    ):
        return {
            "tema": "Entregavel 2 - Interface de Chat",
            "acao": "Conferir historico em session_state, chamada HTTP ao backend e tratamento de erro.",
        }

    if any(
        palavra in texto
        for palavra in ["entregavel 1", "fastapi", "endpoint", "api", "swagger", "backend"]
    ):
        return {
            "tema": "Entregavel 1 - Agente + FastAPI",
            "acao": "Validar rota POST, schema da request/response e separacao entre endpoint e agente.",
        }

    if any(palavra in texto for palavra in ["langgraph", "state", "tool", "llm", "agente"]):
        return {
            "tema": "Orquestracao do agente",
            "acao": "Explicar o papel do State, da Tool, do System Prompt e do no de LLM.",
        }

    if any(
        palavra in texto
        for palavra in ["entregavel 3", "chroma", "rag", "embedding", "retriever"]
    ):
        return {
            "tema": "Entregavel 3 - RAG",
            "acao": "Separar ingestao, busca semantica e uso do contexto pelo agente.",
        }

    return {
        "tema": "Duvida geral do treinamento",
        "acao": "Responder de forma curta e conectar a resposta ao fluxo Streamlit -> FastAPI -> LangGraph.",
    }


if LANGGRAPH_AVAILABLE:

    @tool
    def classificar_pergunta(mensagem: str) -> str:
        """Classifica a pergunta do trainee e sugere qual parte do entregavel usar."""

        return json.dumps(_classificar_texto(mensagem), ensure_ascii=False)

else:

    def classificar_pergunta(mensagem: str) -> str:
        return json.dumps(_classificar_texto(mensagem), ensure_ascii=False)


if LANGGRAPH_AVAILABLE:

    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        tool_context: str


def _executar_tool_classificacao(mensagem: str) -> str:
    if hasattr(classificar_pergunta, "invoke"):
        return classificar_pergunta.invoke({"mensagem": mensagem})
    return classificar_pergunta(mensagem)


def _ultima_mensagem_usuario(messages: list[Any]) -> str:
    for message in reversed(messages):
        role = getattr(message, "type", None)
        if role == "human" or isinstance(message, dict) and message.get("role") == "user":
            return str(getattr(message, "content", None) or message.get("content", ""))
    return ""


def _normalizar_conteudo(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes: list[str] = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                partes.append(str(item["text"]))
            else:
                partes.append(str(item))
        return "\n".join(partes)
    return str(content)


def _build_llm():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY ou GOOGLE_API_KEY para usar o LLM.")

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
    )


def _node_tool_context(state: "AgentState") -> dict[str, str]:
    mensagem = _ultima_mensagem_usuario(state["messages"])
    return {"tool_context": _executar_tool_classificacao(mensagem)}


def _node_llm(state: "AgentState") -> dict[str, list[Any]]:
    prompt_com_contexto = (
        f"{SYSTEM_PROMPT}\n\n"
        "Contexto produzido pela tool classificar_pergunta:\n"
        f"{state.get('tool_context', '')}"
    )

    resposta = _build_llm().invoke(
        [SystemMessage(content=prompt_com_contexto), *state["messages"]]
    )
    return {"messages": [resposta]}


@lru_cache(maxsize=1)
def _build_graph():
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError(f"LangGraph indisponivel: {LANGGRAPH_IMPORT_ERROR}")

    graph = StateGraph(AgentState)
    graph.add_node("classificar_contexto", _node_tool_context)
    graph.add_node("gerar_resposta", _node_llm)
    graph.add_edge(START, "classificar_contexto")
    graph.add_edge("classificar_contexto", "gerar_resposta")
    graph.add_edge("gerar_resposta", END)
    return graph.compile()


def _converter_historico(history: list[dict[str, str]]) -> list[Any]:
    if not LANGGRAPH_AVAILABLE:
        return []

    mensagens: list[Any] = []
    for item in history[-8:]:
        role = item.get("role")
        content = item.get("content", "")

        if not content:
            continue
        if role == "user":
            mensagens.append(HumanMessage(content=content))
        elif role == "assistant":
            mensagens.append(AIMessage(content=content))

    return mensagens


def _resposta_local(message: str) -> str:
    contexto = _classificar_texto(message)
    tema = contexto["tema"]
    acao = contexto["acao"]

    return (
        "Estou em modo local de demonstracao porque o LangGraph/LLM ou a API key "
        "nao estao disponiveis neste ambiente.\n\n"
        f"Tema identificado pela tool: {tema}.\n"
        f"Proximo passo sugerido: {acao}\n\n"
        "Fluxo demonstrado: a tela Streamlit envia a mensagem por HTTP para o "
        "FastAPI, o endpoint chama a camada do agente, a tool classifica a pergunta "
        "e a resposta volta para o chat."
    )


def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagem = message.strip()
    if not mensagem:
        raise ValueError("A mensagem nao pode estar vazia.")

    if not LANGGRAPH_AVAILABLE:
        return _resposta_local(mensagem)

    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return _resposta_local(mensagem)

    mensagens = _converter_historico(history or [])
    mensagens.append(HumanMessage(content=mensagem))

    result = _build_graph().invoke({"messages": mensagens, "tool_context": ""})
    resposta = result["messages"][-1]
    return _normalizar_conteudo(resposta.content)


def status_agente() -> dict[str, Any]:
    llm_configurado = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    modo: Literal["llm", "local"] = "llm" if LANGGRAPH_AVAILABLE and llm_configurado else "local"

    return {
        "agent": "agente_teste",
        "responsibility": "Mentor didatico para entregaveis de orquestracao de IA.",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "langgraph_import_error": None
        if LANGGRAPH_AVAILABLE
        else "Dependencias LangGraph indisponiveis no ambiente.",
        "llm_configured": llm_configurado,
        "model_config": MODEL_CONFIG,
        "mode": modo,
        "tools": ["classificar_pergunta"],
    }
