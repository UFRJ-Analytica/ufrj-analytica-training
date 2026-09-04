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
Voce e o Agente de Estudos da Analytica.

Responsabilidade:
- ajudar trainees a montar os entregaveis 1 e 2 de orquestracao;
- explicar separacao entre Streamlit (frontend), FastAPI (HTTP) e LangGraph (agente);
- sugerir proximos passos praticos para implementacao e validacao.

Regras:
- responda em portugues;
- seja objetivo e didatico;
- nao invente requisitos alem do README da capacitacao.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("SGCONT_MODEL", os.getenv("AGENTE_TESTE_MODEL", "gemini-2.5-flash")),
    "temperature": float(os.getenv("SGCONT_TEMPERATURE", "0.2")),
    "max_output_tokens": int(os.getenv("SGCONT_MAX_OUTPUT_TOKENS", "1024")),
}


def _classificar_pergunta(mensagem: str) -> dict[str, str]:
    texto = mensagem.lower()

    if any(p in texto for p in ["streamlit", "frontend", "chat", "session_state", "historico"]):
        return {
            "tema": "Entregavel 2 - Interface Streamlit",
            "acao": "Manter historico em session_state e chamar o backend por HTTP com tratamento de erro.",
        }

    if any(p in texto for p in ["fastapi", "endpoint", "api", "swagger", "backend"]):
        return {
            "tema": "Entregavel 1 - API do agente",
            "acao": "Conferir rota POST /agent/sgcont/chat e separacao entre endpoint e camada do agente.",
        }

    if any(p in texto for p in ["langgraph", "state", "tool", "llm"]):
        return {
            "tema": "Arquitetura do agente",
            "acao": "Explicar state, tool e no do LLM no fluxo START -> tool -> LLM -> END.",
        }

    return {
        "tema": "Duvida geral de orquestracao",
        "acao": "Conectar a resposta ao fluxo Streamlit -> FastAPI -> LangGraph.",
    }


if LANGGRAPH_AVAILABLE:

    @tool
    def classificar_pergunta(mensagem: str) -> str:
        """Classifica a pergunta para orientar a resposta do agente."""

        return json.dumps(_classificar_pergunta(mensagem), ensure_ascii=False)

else:

    def classificar_pergunta(mensagem: str) -> str:
        return json.dumps(_classificar_pergunta(mensagem), ensure_ascii=False)


if LANGGRAPH_AVAILABLE:

    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        tool_context: str


def _executar_tool(mensagem: str) -> str:
    if hasattr(classificar_pergunta, "invoke"):
        return classificar_pergunta.invoke({"mensagem": mensagem})
    return classificar_pergunta(mensagem)


def _ultima_mensagem_usuario(messages: list[Any]) -> str:
    for item in reversed(messages):
        role = getattr(item, "type", None)
        if role == "human" or (isinstance(item, dict) and item.get("role") == "user"):
            return str(getattr(item, "content", None) or item.get("content", ""))
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
    return {"tool_context": _executar_tool(mensagem)}


def _node_llm(state: "AgentState") -> dict[str, list[Any]]:
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "Contexto da tool classificar_pergunta:\n"
        f"{state.get('tool_context', '')}"
    )

    resposta = _build_llm().invoke([SystemMessage(content=prompt), *state["messages"]])
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
    for item in history[-10:]:
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
    contexto = _classificar_pergunta(message)
    return (
        "Estou em modo local porque LangGraph/LLM ou API key nao estao disponiveis.\n\n"
        f"Tema: {contexto['tema']}\n"
        f"Proximo passo: {contexto['acao']}\n\n"
        "Fluxo esperado: Streamlit -> FastAPI -> LangGraph -> resposta no chat."
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
    return _normalizar_conteudo(result["messages"][-1].content)


def status_agente() -> dict[str, Any]:
    llm_configurado = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    modo: Literal["llm", "local"] = "llm" if LANGGRAPH_AVAILABLE and llm_configurado else "local"

    return {
        "agent": "sgcont",
        "responsibility": "Agente didatico para entregaveis 1 e 2 da orquestracao de IA.",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "langgraph_import_error": LANGGRAPH_IMPORT_ERROR,
        "llm_configured": llm_configurado,
        "model_config": MODEL_CONFIG,
        "mode": modo,
        "tools": ["classificar_pergunta"],
    }
