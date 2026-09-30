"""
Agente de Python (Isaac Vianna).

Assistente especializado em Python: explica a linguagem e a biblioteca
padrao, ensina boas praticas e analisa trechos de codigo enviados pelo
usuario. Usa RAG (ChromaDB) como fonte principal quando ha documentos
relevantes na base de conhecimento.

Nada aqui conecta no ChromaDB ou no Gemini no momento do import: tudo e
inicializado de forma preguicosa (o grafo e compilado uma unica vez na
primeira chamada), para o backend continuar subindo mesmo sem essas
dependencias disponiveis.
"""
from __future__ import annotations

import ast
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND_ENV_FILE)
except ImportError:
    pass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.rag.isaac_vianna_retriever import format_docs, get_retriever

logger = logging.getLogger(__name__)

# Modelo do chat, lido do .env (ver backend/.env, nao versionado).
AGENT_MODEL = os.getenv("ISAAC_VIANNA_AGENT_MODEL", "gemini-2.5-flash")


SYSTEM_PROMPT = """
Voce e o Agente de Python, um assistente especializado na linguagem Python.

Escopo:
- explicar conceitos da linguagem Python e da biblioteca padrao;
- ensinar boas praticas de codigo (PEP 8, PEP 20, PEP 257);
- analisar trechos de codigo Python enviados pelo usuario e ajudar a
  entender erros e mensagens de excecao.

Fora de escopo:
- para qualquer assunto que nao seja Python ou programacao, recuse
  educadamente e redirecione a conversa para duvidas sobre Python.

Idioma:
- responda sempre em portugues do Brasil.

Formato:
- respostas objetivas e diretas;
- sempre que mostrar codigo, use blocos ```python.

Uso da ferramenta:
- quando o usuario enviar um trecho de codigo Python para analise, chame
  a ferramenta `analisar_estrutura` antes de comentar a estrutura do
  codigo.

Regras de contexto (base de conhecimento):
- quando houver documentos de contexto, use-os como fonte principal e
  cite a fonte (nome do arquivo);
- se a pergunta depender da documentacao (PEPs, tutorial, material da
  capacitacao) e a informacao nao estiver no contexto, diga claramente
  que nao encontrou isso na base de conhecimento. Nao invente;
- para ajuda geral de programacao que nao depende da base, voce pode
  responder com seu proprio conhecimento, deixando claro que a resposta
  nao veio da base.
""".strip()


class IsaacViannaState(MessagesState):
    """Estado do grafo: historico de mensagens + contexto recuperado do Chroma."""

    context: str


# ---------------------------------------------------------------------------
# Tool: analisa a estrutura de um trecho de codigo Python sem executa-lo.
# ---------------------------------------------------------------------------

def _tem_bloco_main(arvore: ast.Module) -> bool:
    """Verifica se existe um `if __name__ == "__main__":` no topo do modulo."""
    for node in arvore.body:
        if not isinstance(node, ast.If):
            continue
        teste = node.test
        if (
            isinstance(teste, ast.Compare)
            and isinstance(teste.left, ast.Name)
            and teste.left.id == "__name__"
            and len(teste.comparators) == 1
            and isinstance(teste.comparators[0], ast.Constant)
            and teste.comparators[0].value == "__main__"
        ):
            return True
    return False


@tool
def analisar_estrutura(codigo: str) -> str:
    """Analisa a estrutura de um trecho de codigo Python sem executa-lo.

    Use esta ferramenta sempre que o usuario enviar um trecho de codigo
    Python para revisao. Ela usa o modulo `ast` da biblioteca padrao para
    ler o codigo sem roda-lo e retorna um resumo com: total de linhas,
    imports, funcoes (nome, argumentos, linha e se tem docstring),
    classes (nome, metodos e linha) e se existe um bloco
    `if __name__ == "__main__"`. Se o codigo tiver erro de sintaxe,
    retorna a mensagem, a linha e a coluna do erro.
    """
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as exc:
        return f"Erro de sintaxe: {exc.msg} (linha {exc.lineno}, coluna {exc.offset})"

    imports: list[str] = []
    funcoes: list[str] = []
    classes: list[str] = []

    for node in ast.walk(arvore):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modulo = node.module or ""
            imports.extend(f"{modulo}.{alias.name}" for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            argumentos = ", ".join(arg.arg for arg in node.args.args)
            tem_docstring = ast.get_docstring(node) is not None
            funcoes.append(
                f"- {node.name}({argumentos}) na linha {node.lineno} "
                f"({'com' if tem_docstring else 'sem'} docstring)"
            )
        elif isinstance(node, ast.ClassDef):
            metodos = [
                filho.name
                for filho in node.body
                if isinstance(filho, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append(
                f"- {node.name} na linha {node.lineno}, "
                f"metodos: {', '.join(metodos) if metodos else 'nenhum'}"
            )

    linhas_resumo = [
        f"Total de linhas: {len(codigo.splitlines())}",
        f"Imports: {', '.join(imports) if imports else 'nenhum'}",
        "Funcoes:\n" + "\n".join(funcoes) if funcoes else "Funcoes: nenhuma",
        "Classes:\n" + "\n".join(classes) if classes else "Classes: nenhuma",
        f"Bloco if __name__ == '__main__': {'sim' if _tem_bloco_main(arvore) else 'nao'}",
    ]
    return "\n".join(linhas_resumo)


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def _build_llm():
    """Instancia o modelo Gemini com os parametros do entregavel."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY para usar o Agente de Python.")

    return ChatGoogleGenerativeAI(
        model=AGENT_MODEL,
        temperature=0.2,  # respostas tecnicas e consistentes
        max_output_tokens=2048,
        timeout=60,
        max_retries=2,
        google_api_key=api_key,
    )


# ---------------------------------------------------------------------------
# Nos do grafo
# ---------------------------------------------------------------------------

def _node_retrieve(state: IsaacViannaState) -> dict[str, str]:
    """Busca no ChromaDB o contexto relevante para a ultima pergunta do usuario."""
    ultima_mensagem = state["messages"][-1] if state["messages"] else None
    pergunta = str(getattr(ultima_mensagem, "content", "") or "")

    try:
        documentos = get_retriever().invoke(pergunta)
        contexto = format_docs(documentos)
    except Exception as exc:
        # O Chroma pode estar desligado ou indisponivel: o agente segue sem
        # contexto em vez de quebrar o backend.
        logger.warning("Falha ao consultar o ChromaDB, seguindo sem contexto: %s", exc)
        contexto = ""

    return {"context": contexto}


def _node_agent(state: IsaacViannaState) -> dict[str, list[Any]]:
    """Monta o system prompt com o contexto e chama o LLM (com tools disponiveis)."""
    contexto = state.get("context", "")
    if contexto:
        bloco_contexto = f"## Contexto da base de conhecimento\n{contexto}"
    else:
        bloco_contexto = (
            "## Contexto da base de conhecimento\n"
            "Nenhum documento relevante foi encontrado (ou a base esta indisponivel)."
        )

    prompt_sistema = f"{SYSTEM_PROMPT}\n\n{bloco_contexto}"
    llm_com_tools = _build_llm().bind_tools([analisar_estrutura])
    resposta = llm_com_tools.invoke([SystemMessage(content=prompt_sistema), *state["messages"]])
    return {"messages": [resposta]}


@lru_cache(maxsize=1)
def get_graph():
    """Compila o grafo LangGraph uma unica vez (lazy, via cache)."""
    grafo = StateGraph(IsaacViannaState)
    grafo.add_node("retrieve", _node_retrieve)
    grafo.add_node("agent", _node_agent)
    grafo.add_node("tools", ToolNode([analisar_estrutura]))

    grafo.add_edge(START, "retrieve")
    grafo.add_edge("retrieve", "agent")
    grafo.add_conditional_edges("agent", tools_condition)
    grafo.add_edge("tools", "agent")

    return grafo.compile()


def _normalizar_conteudo(content: Any) -> str:
    """Extrai o texto da resposta do Gemini (que pode vir como lista de partes)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = [
            str(item.get("text", "")) if isinstance(item, dict) else str(item)
            for item in content
        ]
        return "\n".join(parte for parte in partes if parte)
    return str(content)


def run_isaac_vianna_agent(message: str) -> str:
    """Executa o grafo do Agente de Python e retorna o texto da resposta final."""
    resultado = get_graph().invoke({"messages": [HumanMessage(message)], "context": ""})
    ultima_mensagem = resultado["messages"][-1]
    return _normalizar_conteudo(ultima_mensagem.content)
