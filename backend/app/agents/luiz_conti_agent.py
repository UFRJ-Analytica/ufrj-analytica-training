from __future__ import annotations

import ast
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND_ENV_FILE)
except ImportError:
    pass

try:
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langgraph.graph import END, START, StateGraph
    from langgraph.graph.message import add_messages

    LANGGRAPH_AVAILABLE = True
    LANGGRAPH_IMPORT_ERROR = None
except ImportError as exc:
    LANGGRAPH_AVAILABLE = False
    LANGGRAPH_IMPORT_ERROR = str(exc)


SYSTEM_PROMPT = """
Voce e o Agente Python.

Responsabilidade:
- ajudar desenvolvedores com duvidas sobre a linguagem Python;
- explicar sintaxe, boas praticas, estrutura de codigo e bibliotecas padrao;
- responder em portugues, com tom didatico e objetivo;
- quando receber um trecho de codigo, analisar sua estrutura antes de responder.
- sempre busque enviar códigos de exemplos

Regras:
- nao invente comportamento de funcoes ou bibliotecas que voce nao tenha certeza;
- se o codigo enviado tiver erro de sintaxe, informe isso claramente;
- destaque boas praticas relevantes quando isso ajudar na resposta.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("AGENTE_PYTHON_MODEL", "gemini-3.8-flash"),
    "temperature": 0.2,
    "max_output_tokens": 1024,
}


def _extrair_codigo(mensagem: str) -> str | None:
    if "```" not in mensagem:
        return None

    partes = mensagem.split("```")
    if len(partes) < 2:
        return None

    bloco = partes[1]
    if bloco.startswith("python"):
        bloco = bloco[len("python"):]
    return bloco.strip() or None


def _analisar_estrutura(codigo: str) -> dict[str, Any]:
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as exc:
        return {"valido": False, "erro": str(exc)}

    funcoes: list[str] = []
    classes: list[str] = []
    imports: list[str] = []

    for node in ast.walk(arvore):
        if isinstance(node, ast.FunctionDef):
            funcoes.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modulo = node.module or ""
            imports.extend(f"{modulo}.{alias.name}" for alias in node.names)

    return {
        "valido": True,
        "funcoes": funcoes,
        "classes": classes,
        "imports": imports,
    }


if LANGGRAPH_AVAILABLE:

    @tool
    def analisar_estrutura(codigo: str) -> str:
        """Analisa um trecho de codigo Python e retorna funcoes, classes e imports encontrados, ou o erro de sintaxe caso o codigo seja invalido."""

        return json.dumps(_analisar_estrutura(codigo), ensure_ascii=False)

else:

    def analisar_estrutura(codigo: str) -> str:
        return json.dumps(_analisar_estrutura(codigo), ensure_ascii=False)


if LANGGRAPH_AVAILABLE:

    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        tool_context: str


def _executar_tool_analise(codigo: str) -> str:
    if hasattr(analisar_estrutura, "invoke"):
        return analisar_estrutura.invoke({"codigo": codigo})
    return analisar_estrutura(codigo)


def _ultima_mensagem_usuario(messages: list[Any]) -> str:
    for message in reversed(messages):
        role = getattr(message, "type", None)
        if role == "human" or isinstance(message, dict) and message.get("role") == "user":
            return str(getattr(message, "content", None) or message.get("content", ""))
    return ""


def _normalizar_conteudo(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes: list[str] = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                partes.append(str(item["text"]))
            else:
                partes.append(str(item))
        return "\n".join(partes)
    return str(content)


def _build_llm():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
    )


def _node_tool_context(state: "AgentState") -> dict[str, str]:
    mensagem = _ultima_mensagem_usuario(state["messages"])
    codigo = _extrair_codigo(mensagem)

    if codigo is None:
        return {"tool_context": json.dumps({"codigo_detectado": False}, ensure_ascii=False)}

    resultado = json.loads(_executar_tool_analise(codigo))
    resultado["codigo_detectado"] = True
    return {"tool_context": json.dumps(resultado, ensure_ascii=False)}


def _node_llm(state: "AgentState") -> dict[str, list[Any]]:
    prompt_com_contexto = (
        f"{SYSTEM_PROMPT}\n\n"
        "Contexto produzido pela tool analisar_estrutura:\n"
        f"{state.get('tool_context', '')}"
    )

    resposta = _build_llm().invoke(
        [SystemMessage(content=prompt_com_contexto), *state["messages"]]
    )
    return {"messages": [resposta]}


@lru_cache(maxsize=1)
def _build_graph():
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError(f"LangGraph indisponivel: {LANGGRAPH_IMPORT_ERROR}")

    graph = StateGraph(AgentState)
    graph.add_node("analisar_codigo", _node_tool_context)
    graph.add_node("gerar_resposta", _node_llm)
    graph.add_edge(START, "analisar_codigo")
    graph.add_edge("analisar_codigo", "gerar_resposta")
    graph.add_edge("gerar_resposta", END)
    return graph.compile()


def _converter_historico(history: list[dict[str, str]]) -> list[Any]:
    if not LANGGRAPH_AVAILABLE:
        return []

    mensagens: list[Any] = []
    for item in history[-8:]:
        role = item.get("role")
        content = item.get("content", "")

        if not content:
            continue
        if role == "user":
            mensagens.append(HumanMessage(content=content))
        elif role == "assistant":
            mensagens.append(AIMessage(content=content))

    return mensagens


def _resposta_local(message: str) -> str:
    codigo = _extrair_codigo(message)

    if codigo is None:
        return (
            "Estou em modo local de demonstracao porque o LangGraph/LLM ou a API key "
            "nao estao disponiveis neste ambiente.\n\n"
            "Nenhum bloco de codigo foi identificado na mensagem.\n\n"
        )

    analise = _analisar_estrutura(codigo)

    if not analise["valido"]:
        return (
            "Estou em modo local de demonstracao porque o LangGraph/LLM ou a API key "
            "nao estao disponiveis neste ambiente.\n\n"
            f"O codigo enviado possui um erro de sintaxe: {analise['erro']}"
        )

    return (
        "Estou em modo local de demonstracao porque o LangGraph/LLM ou a API key "
        "nao estao disponiveis neste ambiente.\n\n"
        f"Funcoes encontradas: {analise['funcoes']}\n"
        f"Classes encontradas: {analise['classes']}\n"
        f"Imports encontrados: {analise['imports']}"
    )


def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagem = message.strip()
    if not mensagem:
        raise ValueError("A mensagem nao pode estar vazia.")

    if not LANGGRAPH_AVAILABLE:
        return _resposta_local(mensagem)

    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return _resposta_local(mensagem)

    mensagens = _converter_historico(history or [])
    mensagens.append(HumanMessage(content=mensagem))

    result = _build_graph().invoke({"messages": mensagens, "tool_context": ""})
    resposta = result["messages"][-1]
    return _normalizar_conteudo(resposta.content)


def status_agente() -> dict[str, Any]:
    llm_configurado = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    modo: Literal["llm", "local"] = "llm" if LANGGRAPH_AVAILABLE and llm_configurado else "local"

    return {
        "agent": "agente_python",
        "responsibility": "Assistente especializado em programacao Python.",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "langgraph_import_error": LANGGRAPH_IMPORT_ERROR,
        "llm_configured": llm_configurado,
        "model_config": MODEL_CONFIG,
        "mode": modo,
        "tools": ["analisar_estrutura"],
    }