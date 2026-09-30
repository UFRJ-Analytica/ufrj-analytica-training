import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from backend.rag.pedro_ferrari_rag import recuperar_contexto


load_dotenv("backend/.env")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


JOGOS = [
    {
        "nome": "Elden Ring",
        "genero": "RPG de ação",
        "plataformas": ["PC", "PlayStation", "Xbox"],
        "descricao": "Mundo aberto, exploração e combate desafiador."
    },
    {
        "nome": "The Witcher 3",
        "genero": "RPG de ação",
        "plataformas": ["PC", "PlayStation", "Xbox", "Switch"],
        "descricao": "Mundo aberto com história, exploração e decisões."
    },
    {
        "nome": "Stardew Valley",
        "genero": "simulação",
        "plataformas": ["PC", "PlayStation", "Xbox", "Switch", "Mobile"],
        "descricao": "Fazenda, exploração e uma experiência tranquila."
    },
    {
        "nome": "Hades",
        "genero": "roguelike de ação",
        "plataformas": ["PC", "PlayStation", "Xbox", "Switch"],
        "descricao": "Combate rápido e progressão entre tentativas."
    },
    {
        "nome": "Minecraft",
        "genero": "sandbox",
        "plataformas": ["PC", "PlayStation", "Xbox", "Switch", "Mobile"],
        "descricao": "Construção, exploração e sobrevivência."
    },
    {
        "nome": "Hollow Knight",
        "genero": "metroidvania",
        "plataformas": ["PC", "PlayStation", "Xbox", "Switch"],
        "descricao": "Exploração, plataforma e combate."
    },
    {
        "nome": "Celeste",
        "genero": "plataforma",
        "plataformas": ["PC", "PlayStation", "Xbox", "Switch"],
        "descricao": "Plataforma de precisão e fases desafiadoras."
    },
    {
        "nome": "Baldur's Gate 3",
        "genero": "RPG",
        "plataformas": ["PC", "PlayStation", "Xbox"],
        "descricao": "RPG com escolhas, estratégia e combate por turnos."
    }
]


@tool
def buscar_jogos(genero: str = "", plataforma: str = "") -> str:
    """Busca jogos por gênero e/ou plataforma."""

    resultados = []

    for jogo in JOGOS:
        genero_ok = True
        plataforma_ok = True

        if genero:
            genero_ok = genero.lower() in jogo["genero"].lower()

        if plataforma:
            plataforma_ok = False

            for item in jogo["plataformas"]:
                if plataforma.lower() in item.lower():
                    plataforma_ok = True
                    break

        if genero_ok and plataforma_ok:
            resultados.append(jogo)

    if len(resultados) == 0:
        return "Nenhum jogo encontrado com esses filtros."

    texto = ""

    for jogo in resultados:
        texto += (
            f"{jogo['nome']} | "
            f"Gênero: {jogo['genero']} | "
            f"Plataformas: {', '.join(jogo['plataformas'])} | "
            f"{jogo['descricao']}\n"
        )

    return texto


@tool
def consultar_base_jogos(pergunta: str) -> str:
    """Pesquisa informações na base de conhecimento de jogos."""

    return recuperar_contexto(pergunta)


TOOLS = [
    buscar_jogos,
    consultar_base_jogos
]


SYSTEM_PROMPT = """
Você é o GAMEni, um assistente especializado em jogos.

Ajude o usuário a encontrar jogos, comparar opções e receber recomendações.

Considere o histórico da conversa para entender referências como
"esse jogo", "a primeira opção" ou "o anterior".

Use buscar_jogos quando precisar filtrar por gênero ou plataforma.

Use consultar_base_jogos quando precisar consultar características
ou recomendações presentes na base de conhecimento.

Não invente informações que deveriam vir da base de conhecimento.
Se uma informação não estiver disponível, informe isso.

Responda de forma simples e em português.
"""


def criar_llm():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY não encontrada.")

    modelo = os.getenv(
        "PEDRO_FERRARI_MODEL",
        "gemini-3.8-flash"
    )

    llm = ChatGoogleGenerativeAI(
        model=modelo,
        temperature=0.4,
        max_retries=0
    )

    return llm.bind_tools(TOOLS)


def chamar_modelo(state: AgentState):
    llm = criar_llm()

    mensagens = []
    mensagens.append(
        SystemMessage(content=SYSTEM_PROMPT)
    )

    for mensagem in state["messages"]:
        mensagens.append(mensagem)

    resposta = llm.invoke(mensagens)

    return {
        "messages": [resposta]
    }


grafo = StateGraph(AgentState)

grafo.add_node(
    "agent",
    chamar_modelo
)

grafo.add_node(
    "tools",
    ToolNode(TOOLS)
)

grafo.add_edge(
    START,
    "agent"
)

grafo.add_conditional_edges(
    "agent",
    tools_condition
)

grafo.add_edge(
    "tools",
    "agent"
)

agent_graph = grafo.compile()


def normalizar_conteudo(conteudo):
    if isinstance(conteudo, str):
        return conteudo

    if isinstance(conteudo, list):
        texto = ""

        for bloco in conteudo:
            if isinstance(bloco, str):
                texto += bloco

            elif isinstance(bloco, dict):
                if bloco.get("type") == "text":
                    texto += bloco.get("text", "")

        return texto

    return str(conteudo)


def executar_agente(mensagem: str, historico=None) -> str:
    mensagens = []

    if historico:
        for item in historico:

            if item["role"] == "user":
                mensagens.append(
                    HumanMessage(
                        content=item["content"]
                    )
                )

            elif item["role"] == "assistant":
                mensagens.append(
                    AIMessage(
                        content=item["content"]
                    )
                )

    mensagens.append(
        HumanMessage(content=mensagem)
    )

    resultado = agent_graph.invoke(
        {
            "messages": mensagens
        }
    )

    resposta = resultado["messages"][-1].content

    return normalizar_conteudo(resposta)