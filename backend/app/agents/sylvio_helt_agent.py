from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


SYSTEM_PROMPT = """
Você é o Agente Financeiro Educacional.

Seu papel é explicar conceitos de finanças pessoais (juros, inflação, renda fixa,
reserva de emergência, variação de preços) para quem está começando, e fazer
contas simples quando o usuário pedir.

Regras:
- responda em português, de forma curta e com exemplos em reais;
- sempre que a pergunta envolver cálculo, use as tools em vez de calcular de cabeça;
- depois de usar uma tool, explique o resultado em uma ou duas frases;
- você não dá recomendação de investimento (não diga "compre" ou "venda" nada);
- se a pergunta fugir de finanças, diga educadamente que esse não é o seu foco.
""".strip()

MODEL_CONFIG = {
    "model": os.getenv("SYLVIO_HELT_MODEL", "gemini-3.8-flash"),
    "temperature": 0.3,
    "max_output_tokens": 1024,
}


@tool
def calcular_juros_compostos(capital: float, taxa_mensal: float, meses: int) -> str:
    """Calcula quanto um valor rende aplicado a juros compostos.

    capital: valor inicial em reais.
    taxa_mensal: taxa ao mês em porcentagem (ex: 1 para 1% ao mês).
    meses: por quantos meses o dinheiro fica aplicado.
    """
    montante = capital * (1 + taxa_mensal / 100) ** meses
    juros = montante - capital
    return f"Montante final: R$ {montante:.2f} (juros de R$ {juros:.2f})"


@tool
def calcular_variacao_percentual(valor_inicial: float, valor_final: float) -> str:
    """Calcula a variação percentual entre dois valores, como o preço de algo em duas datas."""
    if valor_inicial == 0:
        return "Não é possível calcular variação a partir de zero."
    variacao = (valor_final - valor_inicial) / valor_inicial * 100
    return f"Variação de {variacao:.2f}%"


TOOLS = [calcular_juros_compostos, calcular_variacao_percentual]


class EstadoAgente(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


@lru_cache(maxsize=1)
def _llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no backend/.env")

    llm = ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
        thinking_level="low",
        timeout=60,
        max_retries=1,
    )
    return llm.bind_tools(TOOLS)


def no_agente(estado: EstadoAgente) -> dict:
    mensagens = [SystemMessage(content=SYSTEM_PROMPT), *estado["messages"]]
    resposta = _llm().invoke(mensagens)
    return {"messages": [resposta]}


@lru_cache(maxsize=1)
def _grafo():
    grafo = StateGraph(EstadoAgente)
    grafo.add_node("agente", no_agente)
    grafo.add_node("tools", ToolNode(TOOLS))

    grafo.add_edge(START, "agente")
    # se o LLM pediu uma tool, vai para "tools"; se não, termina
    grafo.add_conditional_edges("agente", tools_condition)
    grafo.add_edge("tools", "agente")
    return grafo.compile()


def _texto(content: Any) -> str:
    # o Gemini às vezes devolve o conteúdo como lista de partes
    if isinstance(content, list):
        return "\n".join(
            parte["text"] if isinstance(parte, dict) and "text" in parte else str(parte)
            for parte in content
        )
    return str(content)


def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagem = message.strip()
    if not mensagem:
        raise ValueError("A mensagem não pode estar vazia.")

    mensagens: list[BaseMessage] = []
    for item in (history or [])[-10:]:
        if item.get("role") == "user":
            mensagens.append(HumanMessage(content=item["content"]))
        elif item.get("role") == "assistant":
            mensagens.append(AIMessage(content=item["content"]))
    mensagens.append(HumanMessage(content=mensagem))

    resultado = _grafo().invoke({"messages": mensagens})
    return _texto(resultado["messages"][-1].content)