import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

@tool
def calcular_media(numeros: list[float]) -> float:
    """Calcula a média aritmética de uma lista de números."""
    if not numeros:
        return 0.0
    return sum(numeros) / len(numeros)

tools = [calcular_media]

# Usando o modelo oficial gemini-1.5-flash
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
    max_retries=5  # Tenta até 5 vezes automaticamente em caso de erro 503
).bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(
    content="Você é um Agente Especialista em Análise de Dados criado por Eduardo Borges. Responda de forma clara e objetiva."
)

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

eduardo_borges_agent = builder.compile()

def run_agent(user_message: str) -> str:
    initial_state = {"messages": [HumanMessage(content=user_message)]}
    result = eduardo_borges_agent.invoke(initial_state)
    
    # Pega o conteúdo da última mensagem retornada
    last_message_content = result["messages"][-1].content
    
    # Trata os casos em que o conteúdo vem em lista de dicionários
    if isinstance(last_message_content, list):
        text_parts = [
            part["text"] for part in last_message_content 
            if isinstance(part, dict) and "text" in part
        ]
        return "\n".join(text_parts)
    
    return str(last_message_content)