"""
Agente de Filmes — implementado com LangGraph.

Responsabilidade: responder perguntas sobre filmes, recomendar títulos e
calcular estatísticas simples (avaliação média, filtros por gênero).

As tools do agente ficam neste mesmo arquivo. Os dados são filmes reais
(título, gênero, ano e avaliação de referência do IMDb), embutidos em
memória, sem depender de arquivo externo.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# --------------------------------------------------------------------------
# Dados e Tools
# --------------------------------------------------------------------------

# Base de filmes reais, com avaliação de referência do IMDb (consultado em
# setembro de 2026). Os nomes seguem o título de exibição no Brasil.
_FILMES = [
    {"titulo": "Um Sonho de Liberdade", "genero": "Drama", "ano": 1994, "avaliacao": 9.3},
    {"titulo": "O Poderoso Chefão", "genero": "Drama", "ano": 1972, "avaliacao": 9.2},
    {"titulo": "Forrest Gump — O Contador de Histórias", "genero": "Drama", "ano": 1994, "avaliacao": 8.8},
    {"titulo": "Clube da Luta", "genero": "Drama", "ano": 1999, "avaliacao": 8.8},
    {"titulo": "Parasita", "genero": "Drama", "ano": 2019, "avaliacao": 8.5},
    {"titulo": "A Origem", "genero": "Ficção Científica", "ano": 2010, "avaliacao": 8.8},
    {"titulo": "Interestelar", "genero": "Ficção Científica", "ano": 2014, "avaliacao": 8.7},
    {"titulo": "Matrix", "genero": "Ficção Científica", "ano": 1999, "avaliacao": 8.7},
    {"titulo": "O Grande Hotel Budapeste", "genero": "Comédia", "ano": 2014, "avaliacao": 8.1},
    {"titulo": "Superbad — É Hoje", "genero": "Comédia", "ano": 2007, "avaliacao": 7.6},
    {"titulo": "Invocação do Mal", "genero": "Terror", "ano": 2013, "avaliacao": 7.5},
    {"titulo": "Hereditário", "genero": "Terror", "ano": 2018, "avaliacao": 7.3},
    {"titulo": "A Viagem de Chihiro", "genero": "Animação", "ano": 2001, "avaliacao": 8.6},
    {"titulo": "Toy Story", "genero": "Animação", "ano": 1995, "avaliacao": 8.3},
    {"titulo": "Mad Max: Estrada da Fúria", "genero": "Ação", "ano": 2015, "avaliacao": 8.1},
    {"titulo": "John Wick", "genero": "Ação", "ano": 2014, "avaliacao": 7.4},
]


def _carregar_filmes() -> pd.DataFrame:
    return pd.DataFrame(_FILMES)


@tool
def buscar_filme(titulo: str) -> str:
    """Busca um filme pelo título (busca parcial, sem diferenciar maiúsculas/minúsculas).

    Args:
        titulo: trecho do título do filme a ser buscado.
    """
    df = _carregar_filmes()
    resultado = df[df["titulo"].str.contains(titulo, case=False, na=False)]
    if resultado.empty:
        return f"Nenhum filme encontrado com o termo '{titulo}'."
    linhas = [
        f"- {r.titulo} ({r.ano}) | Gênero: {r.genero} | Avaliação: {r.avaliacao}/10"
        for r in resultado.itertuples()
    ]
    return "\n".join(linhas)


@tool
def filtrar_por_genero(genero: str) -> str:
    """Lista os filmes disponíveis de um determinado gênero.

    Args:
        genero: nome do gênero (ex: 'Ficção Científica', 'Drama', 'Comédia').
    """
    df = _carregar_filmes()
    resultado = df[df["genero"].str.lower() == genero.strip().lower()]
    if resultado.empty:
        generos_disponiveis = ", ".join(sorted(df["genero"].unique()))
        return (
            f"Nenhum filme encontrado no gênero '{genero}'. "
            f"Gêneros disponíveis: {generos_disponiveis}."
        )
    linhas = [f"- {r.titulo} ({r.ano}) | Avaliação: {r.avaliacao}/10" for r in resultado.itertuples()]
    return "\n".join(linhas)


@tool
def calcular_avaliacao_media(genero: str = "") -> str:
    """Calcula a avaliação média dos filmes da base, geral ou filtrada por gênero.

    Args:
        genero: opcional. Se informado, calcula a média apenas para esse gênero.
    """
    df = _carregar_filmes()
    if genero:
        subset = df[df["genero"].str.lower() == genero.strip().lower()]
        if subset.empty:
            return f"Nenhum filme encontrado no gênero '{genero}' para calcular a média."
        media = subset["avaliacao"].mean()
        return f"Avaliação média dos filmes de {genero}: {media:.2f}/10 (baseado em {len(subset)} filme(s))."
    media = df["avaliacao"].mean()
    return f"Avaliação média geral da base: {media:.2f}/10 (baseado em {len(df)} filmes)."


# --------------------------------------------------------------------------
# Agente (LangGraph)
# --------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é o Agente de Filmes da UFRJ Analytica.

Sua responsabilidade é ajudar o usuário a descobrir, entender e comparar
filmes usando as ferramentas disponíveis:

- buscar_filme: procura um filme pelo título na base local.
- filtrar_por_genero: lista filmes de um gênero específico.
- calcular_avaliacao_media: calcula a avaliação média geral ou por gênero.

Regras:
1. Sempre que a pergunta envolver dados objetivos (título, gênero, nota),
   utilize as ferramentas antes de responder.
2. Nunca invente informações sobre filmes que não estejam nos resultados
   das ferramentas. Se a informação não for encontrada, diga isso
   claramente ao usuário.
3. Responda sempre em português, de forma objetiva e amigável.
"""

TOOLS = [buscar_filme, filtrar_por_genero, calcular_avaliacao_media]


class AgentState(TypedDict):
    """State do LangGraph: histórico de mensagens da conversa."""

    messages: Annotated[list[AnyMessage], add_messages]


def _build_llm() -> ChatGoogleGenerativeAI:
    modelo = os.getenv("AGENTE_FILMES_MODEL", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(
        model=modelo,
        temperature=0.4,
        max_output_tokens=1024,
    )
    return llm.bind_tools(TOOLS)


_llm = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        _llm = _build_llm()
    return _llm


def _agent_node(state: AgentState) -> dict:
    resposta = _get_llm().invoke(state["messages"])
    return {"messages": [resposta]}


def _build_graph():
    grafo = StateGraph(AgentState)
    grafo.add_node("agent", _agent_node)
    grafo.add_node("tools", ToolNode(TOOLS))

    grafo.add_edge(START, "agent")
    grafo.add_conditional_edges("agent", tools_condition)
    grafo.add_edge("tools", "agent")

    return grafo.compile()


_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph


def _extrair_texto(conteudo) -> str:
    """Normaliza o content da mensagem final do LLM para uma string simples.

    Alguns modelos (incluindo versões recentes do Gemini) retornam o content
    como uma lista de blocos (ex: [{'type': 'text', 'text': '...'}]) em vez
    de uma string simples. Esta função extrai apenas o texto desses blocos.
    """
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        partes = []
        for bloco in conteudo:
            if isinstance(bloco, dict):
                if bloco.get("type") == "text" and "text" in bloco:
                    partes.append(bloco["text"])
            elif isinstance(bloco, str):
                partes.append(bloco)
        return "".join(partes) if partes else str(conteudo)
    return str(conteudo)


def run_agent(mensagem: str) -> str:
    """Executa o agente de filmes para uma mensagem do usuário e retorna a resposta em texto."""
    grafo = _get_graph()
    estado_inicial: AgentState = {
        "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=mensagem)]
    }
    resultado = grafo.invoke(estado_inicial)
    ultima_mensagem = resultado["messages"][-1]
    return _extrair_texto(ultima_mensagem.content)
