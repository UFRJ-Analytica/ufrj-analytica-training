from typing import Annotated, TypedDict
from app.rag.retriever import buscar_contexto
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START


@tool
def calcular_imc(peso_kg: float, altura_m: float) -> float:
    """Calcula o IMC usando peso em quilogramas e altura em metros."""
    return peso_kg / (altura_m ** 2)


load_dotenv()


SYSTEM_PROMPT = """
Você é o MyNutri, um agente de orientação nutricional geral.

Sua responsabilidade é responder dúvidas gerais sobre alimentação
e nutrição e realizar cálculos nutricionais simples quando solicitado.

Você deve:
- explicar conceitos básicos de nutrição de forma clara;
- responder dúvidas gerais sobre alimentação;
- utilizar as ferramentas disponíveis quando necessário;
- explicar os resultados dos cálculos de forma simples.

Você não deve:
- diagnosticar doenças;
- prescrever dietas ou tratamentos;
- substituir médicos, nutricionistas ou outros profissionais de saúde;
- fazer recomendações clínicas personalizadas.

Quando uma pergunta exigir diagnóstico, tratamento ou avaliação
individualizada, oriente o usuário a procurar um profissional habilitado.
"""


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.2,
)


class MyNutriAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    context: str


llm_com_tools = llm.bind_tools([calcular_imc])

def recuperar_contexto(state):
    pergunta = state["messages"][-1].content

    contexto = buscar_contexto(pergunta)

    return {
        "context": contexto
    }

def chamar_llm(state):
    contexto = state.get("context", "")

    system_prompt = f"""
{SYSTEM_PROMPT}

BASE DE CONHECIMENTO DO MYNUTRI:

{contexto}

REGRAS SOBRE A BASE DE CONHECIMENTO:

- Utilize a base de conhecimento quando a pergunta estiver relacionada
  às informações disponíveis nela.
- Priorize as informações recuperadas da base.
- Não invente informações que não estejam presentes na base quando
  a pergunta depender de dados específicos da base.
- Se a informação solicitada não estiver disponível na base,
  deixe isso claro para o usuário.
- As fontes podem ser apresentadas ao usuário quando forem relevantes.
"""

    mensagens = [
        SystemMessage(content=system_prompt),
        *state["messages"],
    ]

    resposta = llm_com_tools.invoke(mensagens)

    return {
        "messages": [resposta]
    }

tool_node = ToolNode([calcular_imc])


builder = StateGraph(MyNutriAgentState)

builder.add_node("llm", chamar_llm)
builder.add_node("tools", tool_node)

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)
builder.add_edge("tools", "llm")

graph = builder.compile()


def executar_agente(mensagem: str):
    estado_inicial = {
    "messages": [
        {
            "role": "user",
            "content": mensagem
        }
    ],
    "context": ""
}

    resultado = graph.invoke(estado_inicial)

    return resultado["messages"][-1].content[0]["text"]


if __name__ == "__main__":
    print(
        executar_agente(
            "Tenho 80 kg e 1,80 m. Qual é o meu IMC?"
        )
    )