"""Agente didático de apoio à análise de dados populacionais."""

import json
import os
from functools import lru_cache
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


SYSTEM_PROMPT = """
Você é um tutor de análise de dados da UFRJ Analytica.
Responda sempre em português brasileiro, com clareza e objetividade.
Explique o raciocínio em etapas curtas e não invente números ou fontes.
Quando a pergunta não tiver relação com dados, programação ou população,
responda brevemente e sugira como relacioná-la ao estudo.
""".strip()


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    classification: str


@tool
def identificar_trilha(pergunta: str) -> str:
    """Identifica a trilha de estudo mais adequada para a pergunta."""
    texto = pergunta.casefold()
    if any(term in texto for term in ("sql", "sqlite", "banco", "tabela", "query")):
        trilha = ("Banco de dados", "Responda com SQL legível e explique os relacionamentos.")
    elif any(term in texto for term in ("python", "código", "codigo", "programação", "pandas")):
        trilha = ("Programação e dados", "Prefira exemplos pequenos e explique cada etapa.")
    elif any(term in texto for term in ("população", "populacao", "município", "municipio", "ibge")):
        trilha = ("Análise populacional", "Diferencie métrica, período e unidade de medida.")
    else:
        trilha = ("Fundamentos", "Responda de forma direta e didática.")
    return json.dumps({"trilha": trilha[0], "orientacao": trilha[1]}, ensure_ascii=False)


def _classify(state: AgentState) -> dict[str, str]:
    pergunta = state["messages"][-1].content
    return {"classification": identificar_trilha.invoke({"pergunta": str(pergunta)})}


def _respond(state: AgentState) -> dict[str, list[Any]]:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY ou GOOGLE_API_KEY para usar o agente.")

    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0.2,
        google_api_key=api_key,
    )
    system = f"{SYSTEM_PROMPT}\n\nTrilha identificada:\n{state['classification']}"
    response = llm.invoke([SystemMessage(content=system), *state["messages"]])
    return {"messages": [response]}


@lru_cache(maxsize=1)
def _graph():
    graph = StateGraph(AgentState)
    graph.add_node("identificar_trilha", _classify)
    graph.add_node("responder", _respond)
    graph.add_edge(START, "identificar_trilha")
    graph.add_edge("identificar_trilha", "responder")
    graph.add_edge("responder", END)
    return graph.compile()


def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    """Gera uma resposta considerando as últimas mensagens da conversa."""
    messages: list[BaseMessage] = []
    for item in (history or [])[-8:]:
        content = item.get("content", "").strip()
        if not content:
            continue
        if item.get("role") == "user":
            messages.append(HumanMessage(content=content))
        elif item.get("role") == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=message.strip()))
    result = _graph().invoke({"messages": messages, "classification": ""})
    content = result["messages"][-1].content
    return str(content)
