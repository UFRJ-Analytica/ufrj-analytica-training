import os
from typing import Annotated, TypedDict
import operator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

# 1. Configuração do Modelo
llm = ChatGoogleGenerativeAI(
    model=os.getenv("AGENTE_TESTE_MODEL", "gemini-2.5-flash"), 
    api_key=os.getenv("GEMINI_API_KEY")
)

# 2. Criação das Tools (Foco em Mercado de Energia, Preço e Clima)
def consultar_pld_atual(submercado: str) -> str:
        """Busca o Preço de Liquidação das Diferenças (PLD) atual para um submercado específico (ex: Sudeste/Centro-Oeste)."""
        # Mock para o Entregável 1
        return f"O PLD atual para o submercado {submercado} está fixado no teto estrutural de R$ 682,77/MWh devido à baixa afluência hídrica."

def analisar_impacto_reservatorio_preco(nivel_percentual: float, fenomeno_climatico: str) -> str:
        """Analisa a correlação entre o nível dos reservatórios, fenômenos climáticos e o acionamento térmico."""
        # Mock para o Entregável 1
        if fenomeno_climatico.lower() == "el nino" and nivel_percentual < 50.0:
            return "Alerta: Cenário de El Niño com reservatórios abaixo de 50% indica altíssima probabilidade de acionamento de termelétricas caras, pressionando o preço da energia e a adoção de Bandeira Vermelha."
        return "Cenário hídrico e climático dentro da normalidade para o suprimento de carga atual."

tools = [consultar_pld_atual, analisar_impacto_reservatorio_preco]
llm_with_tools = llm.bind_tools(tools)

# 3. Estado e System Prompt
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

sys_msg = SystemMessage(
    content="Você é um assistente analítico avançado especializado no Mercado de Energia Brasileiro. "
            "Seu foco é analisar a correlação entre níveis de reservatórios, fenômenos climáticos (como o El Niño), "
            "projeções de consumo (carga) e a formação de preços de energia (PLD e Bandeiras Tarifárias). "
            "Sempre que questionado sobre preços ou impactos climáticos na operação do sistema, utilize suas ferramentas para fornecer respostas baseadas em dados."
)

# 4. Nós do Grafo
def call_model(state: AgentState):
    messages = [sys_msg] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "tools"

# 5. Construção do Grafo
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app_graph = workflow.compile()

# Função principal exportada
def run_vanessa_agent(user_message: str) -> str:
    inputs = {"messages": [HumanMessage(content=user_message)]}
    result = app_graph.invoke(inputs)
    return result["messages"][-1].content