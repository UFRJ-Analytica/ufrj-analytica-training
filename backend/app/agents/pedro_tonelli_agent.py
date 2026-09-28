from __future__ import annotations

import json
import os
import re
import statistics
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

try:
    from app.knowledge.pedro_tonelli.retriever import buscar_contexto

    RETRIEVER_AVAILABLE = True
except ImportError:
    RETRIEVER_AVAILABLE = False

    def buscar_contexto(pergunta: str, top_k: int = 3) -> list[dict[str, str]]:
        return []


SYSTEM_PROMPT = """
Voce e o Agente de Analise de Dados da Analytica.

Responsabilidade:
- ajudar a interpretar conjuntos de numeros/dados;
- calcular e explicar estatisticas basicas (media, mediana, desvio padrao);
- explicar conceitos de pandas usando a documentacao oficial recuperada;
- responder em portugues, com tom didatico e objetivo;
- quando a pergunta trouxer uma lista de numeros, usar a estatistica calculada
  pela tool como base da resposta, nunca inventar valores;
- quando houver trechos de documentacao recuperados, usa-los como referencia
  tecnica; se nao houver nada relevante, dizer isso ao usuario em vez de
  inventar.

Regras:
- se a pergunta nao tiver numeros nem relacao com pandas, explicar o que a
  ferramenta faz e pedir um exemplo de dado pra analisar;
- ser direto: primeiro os numeros/fatos, depois uma frase de interpretacao.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("PEDRO_TONELLI_MODEL", "gemini-3.8-flash"),
    "temperature": float(os.getenv("PEDRO_TONELLI_TEMPERATURE", "0.2")),
    "max_output_tokens": int(os.getenv("PEDRO_TONELLI_MAX_OUTPUT_TOKENS", "1024")),
}


def _extrair_numeros(mensagem: str) -> list[float]:
    return [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", mensagem)]


def _calcular_estatisticas(numeros: list[float]) -> dict[str, Any]:
    if not numeros:
        return {"erro": "Nenhum numero encontrado na mensagem."}

    resultado: dict[str, Any] = {
        "quantidade": len(numeros),
        "media": round(statistics.mean(numeros), 4),
        "mediana": round(statistics.median(numeros), 4),
        "minimo": min(numeros),
        "maximo": max(numeros),
    }
    if len(numeros) > 1:
        resultado["desvio_padrao"] = round(statistics.stdev(numeros), 4)

    return resultado


if LANGGRAPH_AVAILABLE:

    @tool
    def calcular_estatisticas(mensagem: str) -> str:
        """Extrai numeros da mensagem e calcula media, mediana, min, max e desvio padrao."""

        numeros = _extrair_numeros(mensagem)
        return json.dumps(_calcular_estatisticas(numeros), ensure_ascii=False)

else:

    def calcular_estatisticas(mensagem: str) -> str:
        numeros = _extrair_numeros(mensagem)
        return json.dumps(_calcular_estatisticas(numeros), ensure_ascii=False)


if LANGGRAPH_AVAILABLE:

    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        tool_context: str
        rag_context: str


def _executar_tool_estatisticas(mensagem: str) -> str:
    if hasattr(calcular_estatisticas, "invoke"):
        return calcular_estatisticas.invoke({"mensagem": mensagem})
    return calcular_estatisticas(mensagem)


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
    return {"tool_context": _executar_tool_estatisticas(mensagem)}


def _node_rag(state: "AgentState") -> dict[str, str]:
    """Busca trechos relevantes da documentacao do pandas no ChromaDB."""
    mensagem = _ultima_mensagem_usuario(state["messages"])

    try:
        chunks = buscar_contexto(mensagem, top_k=3)
    except Exception as exc:
        return {"rag_context": f"(base de conhecimento indisponivel: {exc})"}

    if not chunks:
        return {"rag_context": "(nenhum trecho relevante encontrado na base)"}

    trechos = [
        f"- Fonte: {chunk['fonte']}\n  {chunk['texto'][:400]}" for chunk in chunks
    ]
    return {"rag_context": "\n\n".join(trechos)}


def _node_llm(state: "AgentState") -> dict[str, list[Any]]:
    prompt_com_contexto = (
        f"{SYSTEM_PROMPT}\n\n"
        "Estatisticas calculadas pela tool calcular_estatisticas "
        "(use como fonte, nao invente numeros):\n"
        f"{state.get('tool_context', '')}\n\n"
        "Trechos da documentacao oficial do pandas, recuperados por busca "
        "semantica no ChromaDB (use como referencia tecnica quando fizer "
        "sentido; se nao houver nada relevante, diga isso ao usuario):\n"
        f"{state.get('rag_context', '')}"
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
    graph.add_node("calcular_contexto", _node_tool_context)
    graph.add_node("buscar_rag", _node_rag)
    graph.add_node("gerar_resposta", _node_llm)
    graph.add_edge(START, "calcular_contexto")
    graph.add_edge("calcular_contexto", "buscar_rag")
    graph.add_edge("buscar_rag", "gerar_resposta")
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
    numeros = _extrair_numeros(message)
    stats = _calcular_estatisticas(numeros)

    return (
        "Estou em modo local de demonstracao porque o LangGraph/LLM ou a API key "
        "nao estao disponiveis neste ambiente.\n\n"
        f"Estatisticas calculadas pela tool: {json.dumps(stats, ensure_ascii=False)}\n\n"
        "Fluxo demonstrado: a tela Streamlit envia a mensagem por HTTP para o "
        "FastAPI, o endpoint chama a camada do agente, a tool calcula as "
        "estatisticas, o retriever busca contexto no ChromaDB e a resposta "
        "volta para o chat."
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

    result = _build_graph().invoke(
        {"messages": mensagens, "tool_context": "", "rag_context": ""}
    )
    resposta = result["messages"][-1]
    return _normalizar_conteudo(resposta.content)


def status_agente() -> dict[str, Any]:
    llm_configurado = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    modo: Literal["llm", "local"] = "llm" if LANGGRAPH_AVAILABLE and llm_configurado else "local"

    return {
        "agent": "pedro_tonelli",
        "responsibility": "Agente de analise de dados: calcula estatisticas e responde com apoio de RAG sobre documentacao do pandas.",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "langgraph_import_error": LANGGRAPH_IMPORT_ERROR,
        "llm_configured": llm_configurado,
        "retriever_available": RETRIEVER_AVAILABLE,
        "model_config": MODEL_CONFIG,
        "mode": modo,
        "tools": ["calcular_estatisticas"],
        "knowledge_base": "pedro_tonelli_pandas_docs (ChromaDB)",
    }