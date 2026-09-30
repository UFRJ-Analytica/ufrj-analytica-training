from __future__ import annotations

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
Você é a Assistente Especialista em pesquisa acadêmica com foco em Trabalhos de Conclusão de Curso (TCCs) disponíveis em acesso aberto como no site Oasisbr.

Responsabilidade:
- Orientar estudantes na estruturação de trabalhos acadêmicos e monografias;
- Auxiliar na definição e formatação de títulos acadêmicos;
- Recomendar seções essenciais e tipos de fontes apropriadas por área e tópico de pesquisa;
- Responder com tom didático, objetivo e fundamentado nas normas de pesquisa.

Regras:
- Use as informações de contexto da ferramenta sempre que o usuário perguntar sobre estruturas ou padrões;
- Se a área não for especificada, considere a estrutura ABNT geral;
- Incentive boas práticas de citação e acesso aberto a repositórios públicos.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("AGENTE_TESTE_MODEL", "gemini-2.5-flash"),
    "temperature": 0.2,
    "max_output_tokens": 2048,
}

def _consultar_regras_estrutura(area: str) -> dict[str, str]:
    t = area.lower()
    if any(k in t for k in ["computacao", "computação", "ti", "software", "dados", "ia"]):
        return {
            "area": "Ciência da Computação e Engenharia de Software",
            "padrao_titulos": "Direto e com foco na solução técnica (ex: 'NomeDoSistema: Abordagem para X usando Y')",
            "secoes_principais": "Introdução, Trabalhos Relacionados, Fundamentação Teórica, Metodologia/Arquitetura, Experimentos/Resultados, Conclusão",
            "fontes_recomendadas": "Repositórios Oasisbr, SBC OpenLib, IEEE Xplore, ACM Digital Library e código aberto verificado."
        }
    if any(k in t for k in ["saude", "saúde", "medicina", "enfermagem", "biologia"]):
        return {
            "area": "Ciências da Saúde",
            "padrao_titulos": "Relação explícita entre intervenção/exposição e desfecho (ex: 'Efeitos de X em pacientes com Y')",
            "secoes_principais": "Introdução, Metodologia (Critérios de Inclusão/Amostra), Resultados, Discussão, Considerações Finais",
            "fontes_recomendadas": "Oasisbr, SciELO, PubMed/MEDLINE, Portal de Periódicos CAPES."
        }
    return {
        "area": "Diretriz Geral / Multidisciplinar (ABNT)",
        "padrao_titulos": "Claro, objetivo e delimitado tematicamente (Tema principal : subtítulo explicativo)",
        "secoes_principais": "Introdução (Problema e Objetivos), Revisão de Literatura, Metodologia, Análise dos Dados/Resultados, Conclusões",
        "fontes_recomendadas": "Oasisbr (IBICT), BDTD, repositórios institucionais em acesso aberto."
    }

if LANGGRAPH_AVAILABLE:
    @tool
    def consultar_estrutura_tcc(mensagem: str) -> str:
        """Analisa a dúvida ou tema do usuário e fornece diretrizes de títulos, seções e fontes para o TCC."""
        return json.dumps(_consultar_regras_estrutura(mensagem), ensure_ascii=False)
else:
    def consultar_estrutura_tcc(mensagem: str) -> str:
        return json.dumps(_consultar_regras_estrutura(mensagem), ensure_ascii=False)

if LANGGRAPH_AVAILABLE:
    class AgentState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]
        tool_context: str

def _executar_tool(mensagem: str) -> str:
    if hasattr(consultar_estrutura_tcc, "invoke"):
        return consultar_estrutura_tcc.invoke({"mensagem": mensagem})
    return consultar_estrutura_tcc(mensagem)

def _ultima_mensagem_usuario(messages: list[Any]) -> str:
    for message in reversed(messages):
        role = getattr(message, "type", None)
        if role == "human" or (isinstance(message, dict) and message.get("role") == "user"):
            return str(getattr(message, "content", None) or message.get("content", ""))
    return ""

def _build_llm():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY no arquivo backend/.env")

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
    )

def _node_tool(state: AgentState) -> dict[str, str]:
    mensagem = _ultima_mensagem_usuario(state["messages"])
    return {"tool_context": _executar_tool(mensagem)}

def _node_llm(state: AgentState) -> dict[str, list[Any]]:
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Diretrizes identificadas pela ferramenta para este contexto:\n"
        f"{state.get('tool_context', '')}"
    )
    resposta = _build_llm().invoke([SystemMessage(content=prompt), *state["messages"]])
    return {"messages": [resposta]}

@lru_cache(maxsize=1)
def _build_graph():
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError(f"LangGraph indisponível: {LANGGRAPH_IMPORT_ERROR}")

    graph = StateGraph(AgentState)
    graph.add_node("obter_diretrizes", _node_tool)
    graph.add_node("gerar_resposta", _node_llm)
    graph.add_edge(START, "obter_diretrizes")
    graph.add_edge("obter_diretrizes", "gerar_resposta")
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
    dados = _consultar_regras_estrutura(message)
    return (
        "Modo local de demonstração (LLM ou LangGraph não carregados).\n\n"
        f"Área detectada: {dados['area']}\n"
        f"Padrão de títulos: {dados['padrao_titulos']}\n"
        f"Seções: {dados['secoes_principais']}\n"
        f"Fontes: {dados['fontes_recomendadas']}"
    )

def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagem = message.strip()
    if not mensagem:
        raise ValueError("A mensagem não pode estar vazia.")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not LANGGRAPH_AVAILABLE or not api_key:
        return _resposta_local(mensagem)

    mensagens = _converter_historico(history or [])
    mensagens.append(HumanMessage(content=mensagem))

    result = _build_graph().invoke({"messages": mensagens, "tool_context": ""})
    resposta = result["messages"][-1]
    return str(resposta.content)

def status_agente() -> dict[str, Any]:
    llm_configurado = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    modo: Literal["llm", "local"] = "llm" if LANGGRAPH_AVAILABLE and llm_configurado else "local"

    return {
        "agent": "caroline_nomura",
        "responsibility": "Pesquisa acadêmica, normas e estruturação de TCCs",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "langgraph_import_error": LANGGRAPH_IMPORT_ERROR,
        "llm_configured": llm_configurado,
        "model_config": MODEL_CONFIG,
        "mode": modo,
        "tools": ["consultar_estrutura_tcc"],
    }