from dotenv import load_dotenv
from pathlib import Path
import os
from typing import Literal, Any, TypedDict, Annotated, NotRequired
from functools import lru_cache
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition, InjectedState
from langgraph.types import Command


BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(BACKEND_ENV_FILE)

# Arquivo onde o perfil fica salvo entre uma requisição e outra.
PERFIL_PATH = Path(os.getenv("PROFILE_PATH", "../../dados/perfil.json"))

SYSTEM_PROMPT = """
Você é um assistente pessoal de treinos.

Responsabilidade:
- receber o relato de treinos do usuário (natação, corrida ou musculação);
- estimar o gasto calórico de cada treino;
- sugerir o próximo passo (novo treino ou descanso), considerando o objetivo do
  usuário e os treinos mencionados na conversa.

Regras:
- Se o perfil não tiver peso ou objetivo, pergunte ao usuário e salve com guardar_perfil
  antes de calcular calorias ou sugerir treinos.
- Quando o usuário relatar um treino, use calcular_gasto_calorico e, em seguida, sugira
  o próximo passo.
- Apresente calorias sempre como estimativa.
- Se o usuário relatar dor ou lesão, recomende descanso e procurar um profissional.
- Você não substitui a orientação de um profissional de educação física ou de um médico.
- Responda em português, de forma objetiva.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("AGENTE_TESTE_MODEL", "gemini-3.8-flash"),
    "temperature": float(os.getenv("AGENTE_TESTE_TEMPERATURE", "0.2")),
    "max_output_tokens": int(os.getenv("AGENTE_TESTE_MAX_OUTPUT_TOKENS", "1024")),
}


class Perfil(TypedDict):
    peso_kg: float
    altura: float
    objetivo: str

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    perfil: NotRequired[Perfil] # guarda o peso e o objetivo do usuário


# ---------------------------------------------------------------------------
# Funções internas (lógica pura, chamadas normalmente)
# ---------------------------------------------------------------------------

METS = {"musculacao": 4.5, "natacao": 8.5, "corrida": 11.5, "outro": 7.0}
FATOR_INTENSIDADE = {"leve": 0.9, "moderado": 1.1, "pesado": 1.3}


def _carregar_perfil() -> dict:
    """Lê o perfil salvo em disco. Se não existir ou estiver corrompido, retorna {}."""
    try:
        with open(PERFIL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _salvar_perfil(perfil: dict) -> None:
    PERFIL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PERFIL_PATH, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False)


def _estimar_kcal(modalidade: str, duracao_min: float, intensidade: str, peso_kg: float) -> float:
    # kcal = MET x peso (kg) x tempo (horas)
    horas = duracao_min / 60
    return METS[modalidade] * FATOR_INTENSIDADE[intensidade] * peso_kg * horas


# ---------------------------------------------------------------------------
# Tools (interface do agente)
# ---------------------------------------------------------------------------

@tool
def guardar_perfil(
        peso_kg: Annotated[float, "Peso do usuário em kg"],
        altura: Annotated[float, "Altura do usuário em cm"],
        objetivo: Annotated[str, "Objetivo de treino, ex.: 'correr 10 km'"],
        tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Salva o peso e o objetivo do usuário. Use quando o usuário informar esses dados."""
    perfil = {"peso_kg": peso_kg, "altura": altura, "objetivo": objetivo}
    _salvar_perfil(perfil)  # persiste para as próximas requisições
    return Command(
        update={
            "perfil": perfil,  # atualiza o State desta execução
            "messages": [ToolMessage(content="Perfil salvo.", tool_call_id=tool_call_id)],
        }
    )


@tool
def calcular_gasto_calorico(
        modalidade: Annotated[
            Literal["natacao", "corrida", "musculacao", "outro"], "Modalidade do treino"
        ],
        duracao_min: Annotated[float, "Duração total do treino em minutos"],
        intensidade: Annotated[Literal["leve", "moderado", "pesado"], "Intensidade relatada"],
        state: Annotated[dict, InjectedState],
) -> str:
    """Estima o gasto calórico em kcal de um treino já realizado.
    Use quando o usuário relatar um treino ou pedir as calorias gastas."""
    peso = (state.get("perfil") or {}).get("peso_kg")
    if not peso:
        return "Peso não informado. Peça o peso ao usuário antes de calcular."
    kcal = _estimar_kcal(modalidade, duracao_min, intensidade, peso)
    return f"Estimativa: {kcal:.0f} kcal"


TOOLS = [calcular_gasto_calorico, guardar_perfil]


def _build_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY para usar o LLM.")

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
    )

def _build_llm_com_tools():
    return _build_llm().bind_tools(TOOLS)

def _node_agente(state: AgentState):
    perfil = state.get("perfil") or {}

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Perfil do usuário: {json.dumps(perfil, ensure_ascii=False)}"
        "Se o peso, a altura, e o objetivo de treino do usuário não estiverem no perfil, pergunte antes de calcular calorias."
    )
    resposta = _build_llm_com_tools().invoke([SystemMessage(content=prompt), *state["messages"]])
    return {"messages": [resposta]}

@lru_cache(maxsize=1)
def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agente", _node_agente)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agente")
    graph.add_conditional_edges("agente", tools_condition)
    graph.add_edge("tools", "agente")
    return graph.compile()


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

def _converter_historico(history: list[dict[str, str]]) -> list[Any]:
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

def responder_agente(message: str, history: list[dict[str, str]] | None = None) -> str:
    mensagem = message.strip()
    if not mensagem:
        raise ValueError("A mensagem não pode estar vazia.")

    mensagens = _converter_historico(history or [])
    mensagens.append(HumanMessage(content=mensagem))

    perfil = _carregar_perfil()

    """ inicialmente, o perfil está vazio """
    result = _build_graph().invoke({"messages": mensagens, "perfil": perfil or {}})
    resposta = result["messages"][-1]
    return _normalizar_conteudo(resposta.content)


def status_agente() -> dict[str, Any]:
    llm_configurado = bool(os.getenv("GEMINI_API_KEY"))

    return {
        "agent": "treinador_pessoal",
        "responsibility": "Assistente pessoal de atividades físicas",
        "llm_configured": llm_configurado,
        "model_config": MODEL_CONFIG,
        "tools": [t.name for t in TOOLS],
        "perfil_salvo": bool(_carregar_perfil()),
    }