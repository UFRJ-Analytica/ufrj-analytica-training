from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.tools import tool

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from backend.app.knowledge.julio_menescal.retriever import buscar_contexto

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2]/".env"
load_dotenv(BACKEND_ENV_FILE)

SYSTEM_PROMPT = """
Voce e um Agente Financeiro Educacional.

Responsabilidade:
- explicar conceitos financeiros de forma didatica e objetiva;
- auxiliar o usuario a compreender juros, retornos, variacoes percentuais e outros conceitos financeiros;
- utilizar as ferramentas disponiveis quando forem necessarios calculos;
- explicar de forma clara o significado dos resultados calculados.

Regras:
- sua finalidade e exclusivamente educacional;
- nao apresente recomendacoes personalizadas de compra ou venda de ativos;
- nao invente valores, taxas ou dados que nao tenham sido fornecidos;
- quando faltarem dados necessarios para um calculo, informe quais dados sao necessarios;
- quando uma ferramenta for utilizada, interprete o resultado para o usuario.
- interprete unidades de tempo compativeis como periodos da ferramenta;
- por exemplo, uma taxa de 10% ao mes durante 3 meses corresponde a 3 periodos;
- uma taxa de 8% ao ano durante 5 anos corresponde a 5 periodos;
- se a unidade da taxa e a unidade do tempo forem diferentes, nao faca conversoes sem informacoes suficientes;
""".strip()

MODEL_CONFIG = {
    "model": os.getenv("JULIO_MENESCAL_MODEL", "gemini-3.6-flash"),
    "temperature": float(
        os.getenv("JULIO_MENESCAL_TEMPERATURE", "0.2")
    ),
    "max_output_tokens": int(
        os.getenv("JULIO_MENESCAL_MAX_OUTPUT_TOKENS", "1024")
    ),
}

@tool
def calcular_juros_compostos(
    capital_inicial: float,
    taxa_percentual: float,
    periodos: int,) -> str:

    """
    Calcula o montante final usando juros compostos.

    Use esta ferramenta quando a taxa e o tempo estiverem na mesma unidade.

    Exemplos:
    - 10% ao mes durante 3 meses -> periodos=3
    - 8% ao ano durante 5 anos -> periodos=5
    - 2% por periodo durante 10 periodos -> periodos=10

    A taxa_percentual representa a taxa de cada periodo.
    """

    if capital_inicial < 0:
        return "Erro: o capital inicial nao pode ser negativo."

    if periodos < 0:
        return "Erro: o numero de periodos nao pode ser negativo."

    taxa_decimal = taxa_percentual / 100

    montante = capital_inicial * (1 + taxa_decimal) ** periodos
    juros = montante - capital_inicial

    return (
        f"Montante final: R$ {montante:.2f}. "
        f"Juros acumulados: R$ {juros:.2f}."
    )

@tool
def calcular_variacao_percentual(
    valor_inicial: float,
    valor_final: float,
) -> str:
    """Calcula a variacao percentual entre um valor inicial e um valor final."""

    if valor_inicial == 0:
        return "Erro: o valor inicial nao pode ser zero."

    variacao = ((valor_final - valor_inicial) / valor_inicial) * 100

    return f"Variacao percentual: {variacao:.2f}%."

TOOLS = [calcular_juros_compostos, calcular_variacao_percentual,]

def build_llm():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nao configurada.")


    llm = ChatGoogleGenerativeAI(
    model=MODEL_CONFIG["model"],
    temperature=MODEL_CONFIG["temperature"],
    max_output_tokens=MODEL_CONFIG["max_output_tokens"],
    google_api_key=api_key,)

    return llm.bind_tools(TOOLS)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    contexto_rag: str

def node_retriever(state: AgentState):
    ultima_mensagem = state["messages"][-1]

    pergunta = str(ultima_mensagem.content)

    resultados = buscar_contexto(
        pergunta,
        quantidade=3,
    )

    contexto = "\n\n".join(
        resultado["texto"]
        for resultado in resultados
    )

    return {
        "contexto_rag": contexto
    }

def node_agent(state: AgentState):
    contexto_rag = state.get("contexto_rag", "")

    system_prompt_com_contexto = (
        f"{SYSTEM_PROMPT}\n\n"
        "CONTEXTO RECUPERADO DA BASE DE CONHECIMENTO:\n"
        f"{contexto_rag}\n\n"
        "Quando o contexto recuperado for relevante para a pergunta, "
        "utilize-o para fundamentar a resposta. "
        "Nao invente informacoes que nao estejam no contexto quando a "
        "pergunta depender da base de conhecimento."
    )

    mensagens = [
        SystemMessage(content=system_prompt_com_contexto),
        *state["messages"],
    ]

    resposta = build_llm().invoke(mensagens)

    return {"messages": [resposta]}

tool_node = ToolNode(TOOLS)

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retriever", node_retriever)
    graph.add_node("agent", node_agent)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "retriever")
    graph.add_edge("retriever", "agent")

    graph.add_conditional_edges(
        "agent",
        tools_condition,
    )

    graph.add_edge("tools", "agent")

    return graph.compile()

def extrair_texto(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        partes = []

        for item in content:
            if isinstance(item, dict) and "text" in item:
                partes.append(str(item["text"]))

        return "\n".join(partes)

    return str(content)

def responder_agente(
    message: str,
    history: list[dict[str, str]] | None = None,) -> str:
    mensagem = message.strip()

    if not mensagem:
        raise ValueError("A mensagem nao pode estar vazia.")

    mensagens = []

    for item in history or []:
        role = item.get("role")
        content = item.get("content", "")

        if not content:
            continue

        if role == "user":
            mensagens.append(HumanMessage(content=content))
        elif role == "assistant":
            mensagens.append(AIMessage(content=content))

    mensagens.append(HumanMessage(content=mensagem))

    estado_inicial = {
    "messages": mensagens,
    "contexto_rag": "",}

    resultado = build_graph().invoke(estado_inicial)

    resposta_final = resultado["messages"][-1]

    return extrair_texto(resposta_final.content)