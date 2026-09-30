import os
import json
from typing import Annotated, Any, TypedDict
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

SYSTEM_PROMPT = """
Você é um professor de tecnologia e análise de dados.
Responda em português brasileiro de forma clara, objetiva e didática.
""".strip()

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    tool_context: str

@tool
def classificar_assunto(mensagem: str) -> str:
    """Classifica a pergunta do aluno em uma categoria de estudo."""
    texto = mensagem.lower()
    if any(palavra in texto for palavra in ["código", "python", "programação", "fastapi"]):
        return json.dumps({"categoria": "Programação", "acao": "Explicar lógica e código estruturado."}, ensure_ascii=False)
    return json.dumps({"categoria": "Dúvida Geral", "acao": "Responder de forma direta."}, ensure_ascii=False)

def _node_tool_context(state: AgentState) -> dict[str, str]:
    ultima_mensagem = state["messages"][-1].content
    contexto = classificar_assunto.invoke({"mensagem": ultima_mensagem})
    return {"tool_context": contexto}

def _node_llm(state: AgentState) -> dict[str, list[Any]]:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, google_api_key=api_key)
    
    prompt_com_contexto = f"{SYSTEM_PROMPT}\n\nContexto da classificação (Ferramenta):\n{state.get('tool_context', '')}"
    mensagens = [SystemMessage(content=prompt_com_contexto)] + state["messages"]
    
    resposta = llm.invoke(mensagens)
    return {"messages": [resposta]}

def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analisar_contexto", _node_tool_context)
    graph.add_node("gerar_resposta", _node_llm)
    graph.add_edge(START, "analisar_contexto")
    graph.add_edge("analisar_contexto", "gerar_resposta")
    graph.add_edge("gerar_resposta", END)
    return graph.compile()

def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagens_history = []
    for item in (history or [])[-6:]:
        if item.get("role") == "user":
            mensagens_history.append(HumanMessage(content=item.get("content", "")))
        elif item.get("role") == "assistant":
            mensagens_history.append(AIMessage(content=item.get("content", "")))
    
    mensagens_history.append(HumanMessage(content=message))
    
    grafo = _build_graph()
    resultado = grafo.invoke({"messages": mensagens_history, "tool_context": ""})
    return resultado["messages"][-1].content