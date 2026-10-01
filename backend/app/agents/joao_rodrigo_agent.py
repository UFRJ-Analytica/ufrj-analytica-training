import os
from pathlib import Path
from dotenv import load_dotenv

# carrega o .env que fica 3 niveis acima na pasta principal
root_dir = Path(__file__).resolve().parents[3]
load_dotenv(root_dir / ".env")

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# essa tool nao é muito util em producao mas serve para os propositos de teste 
@tool
def sugerir_musica_por_genero(genero: str) -> str:
    """Aciona a busca por recomendações musicais baseadas em gênero."""
    return f"Sugira uma música aleatória e interessante do gênero {genero}, explicando o motivo da escolha com base no seu conhecimento geral."

tools = [sugerir_musica_por_genero]

llm = ChatGoogleGenerativeAI(
    model=os.getenv("AGENTE_TESTE_MODEL", "gemini-3.8-flash"),
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
).bind_tools(tools)

SYSTEM_PROMPT_TEXT = """
Você é um amigo desempregado e nerd musical. Pedante com gêneros, gosta de som cult e adora corrigir os outros. 
Seu objetivo é recomendar músicas, ajudando o usuario na descoberta musical,
e responder dúvidas sobre artistas, álbuns e história com embasamento cultural.
Seja criativo nas sugestões e explore várias épocas.
Nunca invente dados quantitativos.
Sempre recomende mais de uma música.
Sempre que o usuário pedir uma recomendação por gênero, utilize a ferramenta adequada.
Se não souber a resposta sobre um fato histórico, informe que não possui a informação.
Mantenha um tom amigável e levemente provocativo.
Seja criativo ao sugerir músicas, explorando diferentes épocas do gênero solicitado.
""".strip()

SYSTEM_PROMPT = SystemMessage(content=SYSTEM_PROMPT_TEXT)

def call_model(state: AgentState):
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

joao_rodrigo_agent = builder.compile()

def responder_agente(message: str) -> str:
    initial_state = {"messages": [HumanMessage(content=message)]}
    result = joao_rodrigo_agent.invoke(initial_state)

    content = result["messages"][-1].content

    if isinstance(content, list):
        return "\n".join(
            item["text"]
            for item in content
            if item.get("type") == "text"
        )

    return content