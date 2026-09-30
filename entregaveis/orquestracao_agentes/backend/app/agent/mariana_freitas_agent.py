import os
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.rag.retriever_mariana import buscar_contexto


load_dotenv("../../backend/.env")


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    context: str


@tool
def calcular_media(valores: list[float]) -> float:
    """Calcula a média aritmética de uma lista de números."""

    if not valores:
        raise ValueError("A lista de valores não pode estar vazia.")

    return sum(valores) / len(valores)


tools = [calcular_media]


llm = ChatGoogleGenerativeAI(
    model=os.getenv(
        "AGENTE_TESTE_MODEL",
        "gemini-3.8-flash"
    ),
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """
Você é um agente especializado em análise de dados.

Sua responsabilidade é ajudar o usuário a:
- interpretar dados;
- explicar conceitos estatísticos;
- realizar cálculos simples;
- compreender resultados de análises de dados.

Você possui acesso a uma base de conhecimento sobre análise de dados
e Pandas. Quando houver contexto recuperado da base, utilize-o para
fundamentar sua resposta.

Não invente informações que não estejam nos dados fornecidos ou no
contexto recuperado.

Quando for necessário calcular uma média, utilize a ferramenta
calcular_media.

Responda de forma clara, objetiva e didática.
"""


def retriever_node(state: AgentState):

    pergunta = state["messages"][-1].content

    contexto = buscar_contexto(pergunta)

    return {
        "context": contexto
    }


def agent_node(state: AgentState):

    response = llm_with_tools.invoke(
        [
            (
                "system",
                SYSTEM_PROMPT
                + "\n\nContexto recuperado da base de conhecimento:\n"
                + state["context"]
            ),
            *state["messages"],
        ]
    )

    return {
        "messages": [response]
    }


graph = StateGraph(AgentState)


graph.add_node(
    "retriever",
    retriever_node
)

graph.add_node(
    "agent",
    agent_node
)

graph.add_node(
    "tools",
    ToolNode(tools)
)


graph.set_entry_point("retriever")


graph.add_edge(
    "retriever",
    "agent"
)


graph.add_conditional_edges(
    "agent",
    tools_condition
)


graph.add_edge(
    "tools",
    "agent"
)


agent = graph.compile()


def chat(message: str) -> str:

    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content=message)
            ],
            "context": ""
        }
    )

    content = result["messages"][-1].content

    if isinstance(content, list):

        return "".join(
            item["text"]
            for item in content
            if isinstance(item, dict)
            and "text" in item
        )

    return content