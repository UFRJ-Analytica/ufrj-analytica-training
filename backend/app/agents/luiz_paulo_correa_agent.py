from __future__ import annotations

import json
import os
import re
import unicodedata
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

BACKEND_DIR = Path(__file__).resolve().parents[2]
ARQUIVO_ARTIGOS = BACKEND_DIR / "data" / "luiz_paulo_correa" / "artigos_ciencia_de_dados.json"
load_dotenv(BACKEND_DIR / ".env")

SYSTEM_PROMPT = """
Voce e o Agente de Pesquisa Academica da Analytica.

Responsabilidade:
- ajudar o usuario a encontrar e entender artigos de uma colecao sobre
  ciencia de dados (machine learning, deep learning, NLP, clusterizacao,
  selecao de atributos, series temporais, grafos e visualizacao de dados);
- usar a ferramenta buscar_por_tema sempre que a pergunta envolver encontrar,
  listar ou comparar artigos;
- explicar o conteudo dos artigos encontrados em portugues, de forma didatica,
  mesmo que o titulo e o resumo estejam em ingles.

Regras:
- responda apenas com base nos artigos devolvidos pela ferramenta;
- nunca invente titulo de artigo; se a busca nao retornar nada, diga
  claramente que a colecao nao tem artigos sobre aquele tema e sugira temas
  proximos que existem na colecao de artigos;
- a colecao contem apenas titulo e resumo de cada artigo. Nao ha informacao de
  autor, ano de publicacao, DOI ou link. Se perguntarem qualquer um desses
  dados, responda que a colecao nao guarda essa informacao, em vez de inventar;
- a colecao e selecionada, nao e a literatura completa da area. Deixe isso
  claro quando a pergunta sugerir uma revisao ampla do estado da arte;
- ao citar um artigo, use o titulo exato como veio da ferramenta.
""".strip()

MODEL_CONFIG = {
    "model": os.getenv("LUIZ_PAULO_MODEL", "gemini-3.8-flash"),
    "temperature": float(os.getenv("LUIZ_PAULO_TEMPERATURE", "0.2")),  # factual, nao criativo
    "max_output_tokens": int(os.getenv("LUIZ_PAULO_MAX_OUTPUT_TOKENS", "1024")),
}

MAX_ARTIGOS_POR_BUSCA = 5
MAX_CARACTERES_RESUMO = 700


def _normalizar(texto: Any) -> str:
    """Minusculas e sem acento, para 'Clusterizacao' casar com 'clustering'."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


@lru_cache(maxsize=1)
def _carregar_artigos() -> tuple[dict[str, Any], ...]:
    return tuple(json.loads(ARQUIVO_ARTIGOS.read_text(encoding="utf-8")))


def _relevancia(artigo: dict[str, Any], termo: str) -> int:
    """compara as tags do artigo vale mais que no titulo, que vale mais que no resumo.

    sem isso, um artigo de Random Forest que menciona "clustering" 
    no resumo aparece antes dos que os q sao de fato sobre clusterizacao.
    """
    if termo in _normalizar(" ".join(artigo.get("temas", []))):
        return 3
    if termo in _normalizar(artigo.get("titulo", "")):
        return 2
    if termo in _normalizar(artigo.get("resumo", "")):
        return 1
    return 0


@tool
def buscar_por_tema(tema: str) -> str:
    """busca artigos da colecao de ciencia de dados por tema ou palavra-chave."""
    termo = _normalizar(tema)
    artigos = _carregar_artigos()

    ranqueados = sorted(
        ((_relevancia(a, termo), a) for a in artigos),
        key=lambda par: par[0],
        reverse=True,
    )
    encontrados = [a for nota, a in ranqueados[:MAX_ARTIGOS_POR_BUSCA] if nota > 0]

    if not encontrados:
        temas = sorted({t for a in artigos for t in a.get("temas", [])})
        return f"Nenhum artigo da colecao trata de '{tema}'. Temas disponiveis: {', '.join(temas)}."

    linhas = [f"{len(encontrados)} artigo(s) encontrado(s) para '{tema}':"]
    for artigo in encontrados:
        resumo = artigo["resumo"]
        if len(resumo) > MAX_CARACTERES_RESUMO:
            resumo = resumo[:MAX_CARACTERES_RESUMO].rstrip() + "..."
        linhas.append(
            f"\nTitulo: {artigo['titulo']}"
            f"\nTemas: {', '.join(artigo.get('temas', []))}"
            f"\nResumo: {resumo}"
        )
    return "\n".join(linhas)


TOOLS = [buscar_por_tema]


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


@lru_cache(maxsize=1)
def _llm():
    return ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GEMINI_API_KEY"), **MODEL_CONFIG
    ).bind_tools(TOOLS)


def _node_agent(state: AgentState) -> dict[str, list[Any]]:
    mensagens = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    return {"messages": [_llm().invoke(mensagens)]}


@lru_cache(maxsize=1)
def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", _node_agent)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    # O proprio LLM decide se precisa da tool; tools_condition encerra quando nao.
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()


def _extrair_texto(content: Any) -> str:
    """O Gemini as vezes devolve o content como lista de partes."""
    if isinstance(content, list):
        return "\n".join(
            str(item.get("text", item)) if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)


def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagem = message.strip()
    if not mensagem:
        raise ValueError("A mensagem nao pode estar vazia.")

    tipo_por_papel = {"user": HumanMessage, "assistant": AIMessage}
    mensagens: list[BaseMessage] = [
        tipo_por_papel[item["role"]](content=item["content"])
        for item in (history or [])[-8:]
        if item.get("role") in tipo_por_papel and item.get("content")
    ]
    mensagens.append(HumanMessage(content=mensagem))

    resultado = _build_graph().invoke({"messages": mensagens})
    return _extrair_texto(resultado["messages"][-1].content)


def status_agente() -> dict[str, Any]:
    return {
        "agent": "luiz_paulo_correa",
        "responsibility": "Pesquisa academica sobre uma colecao de artigos de ciencia de dados.",
        "llm_configured": bool(os.getenv("GEMINI_API_KEY")),
        "model_config": MODEL_CONFIG,
        "tools": ["buscar_por_tema"],
        "artigos_carregados": len(_carregar_artigos()),
    }
