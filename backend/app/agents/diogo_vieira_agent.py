"""
Agente de Games (Entregável 1 - Orquestração de IA).

Fluxo do LangGraph:

    START -> agente (LLM) -> precisa de tool? -- sim --> tools -> volta ao agente
                                  |
                                  +-- não --> END

- State: lista de mensagens (histórico + chamadas e resultados de tools).
- Tools: buscar_jogo, filtrar_por_genero, filtrar_por_plataforma.
- Dados: um pequeno catálogo de jogos escrito neste arquivo (sem RAG).
"""
import json
import os
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# backend/.env  (este arquivo está em backend/app/agents/)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


# ---------------------------------------------------------------------------
# Catálogo de jogos (fonte de dados das tools)
# ---------------------------------------------------------------------------
CATALOGO: list[dict[str, Any]] = [
    {"nome": "The Legend of Zelda: Breath of the Wild", "ano": 2017, "desenvolvedora": "Nintendo",
     "generos": ["aventura", "ação", "mundo aberto"], "plataformas": ["Nintendo Switch", "Wii U"]},
    {"nome": "Super Mario Odyssey", "ano": 2017, "desenvolvedora": "Nintendo",
     "generos": ["plataforma", "aventura"], "plataformas": ["Nintendo Switch"]},
    {"nome": "Hollow Knight", "ano": 2017, "desenvolvedora": "Team Cherry",
     "generos": ["metroidvania", "plataforma", "ação"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One"]},
    {"nome": "Celeste", "ano": 2018, "desenvolvedora": "Maddy Makes Games",
     "generos": ["plataforma"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One"]},
    {"nome": "Stardew Valley", "ano": 2016, "desenvolvedora": "ConcernedApe",
     "generos": ["simulação", "rpg"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One", "Mobile"]},
    {"nome": "The Witcher 3: Wild Hunt", "ano": 2015, "desenvolvedora": "CD Projekt Red",
     "generos": ["rpg", "ação", "mundo aberto"],
     "plataformas": ["PC", "PlayStation 4", "Xbox One", "Nintendo Switch"]},
    {"nome": "Elden Ring", "ano": 2022, "desenvolvedora": "FromSoftware",
     "generos": ["rpg", "ação", "mundo aberto"],
     "plataformas": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series"]},
    {"nome": "Hades", "ano": 2020, "desenvolvedora": "Supergiant Games",
     "generos": ["roguelike", "ação"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series"]},
    {"nome": "God of War (2018)", "ano": 2018, "desenvolvedora": "Santa Monica Studio",
     "generos": ["ação", "aventura"], "plataformas": ["PlayStation 4", "PC"]},
    {"nome": "Portal 2", "ano": 2011, "desenvolvedora": "Valve",
     "generos": ["puzzle", "aventura"], "plataformas": ["PC", "PlayStation 3", "Xbox 360"]},
    {"nome": "Minecraft", "ano": 2011, "desenvolvedora": "Mojang Studios",
     "generos": ["sandbox", "sobrevivência"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One", "Mobile"]},
    {"nome": "Civilization VI", "ano": 2016, "desenvolvedora": "Firaxis Games",
     "generos": ["estratégia"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One"]},
    {"nome": "Rocket League", "ano": 2015, "desenvolvedora": "Psyonix",
     "generos": ["esporte", "corrida"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One"]},
    {"nome": "Forza Horizon 5", "ano": 2021, "desenvolvedora": "Playground Games",
     "generos": ["corrida", "mundo aberto"], "plataformas": ["Xbox One", "Xbox Series", "PC"]},
    {"nome": "Disco Elysium", "ano": 2019, "desenvolvedora": "ZA/UM",
     "generos": ["rpg", "narrativa"],
     "plataformas": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series", "Nintendo Switch"]},
    {"nome": "Resident Evil 4 (remake)", "ano": 2023, "desenvolvedora": "Capcom",
     "generos": ["terror", "ação"],
     "plataformas": ["PC", "PlayStation 4", "PlayStation 5", "Xbox Series"]},
    {"nome": "Undertale", "ano": 2015, "desenvolvedora": "Toby Fox",
     "generos": ["rpg", "narrativa"],
     "plataformas": ["PC", "Nintendo Switch", "PlayStation 4", "Xbox One"]},
]

GENEROS = sorted({g for jogo in CATALOGO for g in jogo["generos"]})
PLATAFORMAS = sorted({p for jogo in CATALOGO for p in jogo["plataformas"]})

# apelidos comuns -> nome usado no catálogo (já normalizado)
ALIAS_PLATAFORMAS = {
    "ps4": "playstation 4",
    "ps5": "playstation 5",
    "ps3": "playstation 3",
    "switch": "nintendo switch",
    "xbox series x": "xbox series",
    "xbox series s": "xbox series",
    "computador": "pc",
    "windows": "pc",
    "celular": "mobile",
}


def _norm(texto: str) -> str:
    """Minúsculas e sem acentos, para comparar textos com tolerância."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def _resumo(jogo: dict[str, Any]) -> dict[str, Any]:
    return {
        "nome": jogo["nome"],
        "ano": jogo["ano"],
        "desenvolvedora": jogo["desenvolvedora"],
        "generos": jogo["generos"],
        "plataformas": jogo["plataformas"],
    }


def _json(dados: dict[str, Any]) -> str:
    return json.dumps(dados, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def buscar_jogo(nome: str) -> str:
    """Busca jogos do catálogo pelo nome (parcial, sem diferenciar maiúsculas ou acentos).
    Retorna em JSON os dados do jogo: ano, desenvolvedora, gêneros e plataformas."""
    alvo = _norm(nome)
    achados = [_resumo(j) for j in CATALOGO if alvo and alvo in _norm(j["nome"])]
    if not achados:
        return _json({"encontrados": [], "aviso": "Nenhum jogo do catálogo tem esse nome."})
    return _json({"encontrados": achados})


@tool
def filtrar_por_genero(genero: str) -> str:
    """Lista os jogos do catálogo de um gênero (ex.: rpg, ação, plataforma, puzzle, terror).
    Retorna em JSON os jogos com ano e plataformas."""
    alvo = _norm(genero)
    # compara palavras inteiras: "acao" não pode casar com "simulacao"
    achados = [
        _resumo(j)
        for j in CATALOGO
        if any(alvo and (alvo == _norm(g) or alvo in _norm(g).split()) for g in j["generos"])
    ]
    if not achados:
        return _json({"encontrados": [], "aviso": f"Nenhum jogo do gênero '{genero}' no catálogo.",
                      "generos_disponiveis": GENEROS})
    return _json({"encontrados": achados})


@tool
def filtrar_por_plataforma(plataforma: str) -> str:
    """Lista os jogos do catálogo disponíveis em uma plataforma
    (ex.: PC, Nintendo Switch, PlayStation 5, Xbox Series, Mobile).
    Retorna em JSON os jogos com ano e gêneros."""
    alvo = ALIAS_PLATAFORMAS.get(_norm(plataforma), _norm(plataforma))
    achados = [
        _resumo(j) for j in CATALOGO if any(alvo and alvo in _norm(p) for p in j["plataformas"])
    ]
    if not achados:
        return _json({"encontrados": [], "aviso": f"Nenhum jogo para '{plataforma}' no catálogo.",
                      "plataformas_disponiveis": PLATAFORMAS})
    return _json({"encontrados": achados})


TOOLS = [buscar_jogo, filtrar_por_genero, filtrar_por_plataforma]


# ---------------------------------------------------------------------------
# System Prompt e configuração do modelo
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = f"""
Você é o Game Advisor, um agente especialista em videogames.

Responsabilidade:
- recomendar e explicar jogos usando o catálogo interno, acessado pelas tools;
- ajudar o usuário a achar jogos por nome, gênero ou plataforma;
- responder em português do Brasil, com tom amigável e objetivo.

Regras:
- sempre que a pergunta envolver jogos específicos, gênero ou plataforma, use as tools antes de responder;
- recomende apenas jogos retornados pelas tools; se nada for encontrado, diga isso e sugira algo parecido do catálogo;
- não invente jogos, notas, preços ou datas que não vieram das tools;
- pode explicar conceitos gerais (o que é um roguelike, por exemplo), deixando claro que é uma explicação geral;
- prefira listas curtas, com no máximo 5 jogos por resposta;
- se a pergunta não for sobre games, diga educadamente que só ajuda com esse assunto.

Catálogo disponível:
- gêneros: {", ".join(GENEROS)};
- plataformas: {", ".join(PLATAFORMAS)}.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("GAMES_AGENT_MODEL", "gemini-3.8-flash"),
    "temperature": float(os.getenv("GAMES_AGENT_TEMPERATURE", "0.3")),
    "max_output_tokens": int(os.getenv("GAMES_AGENT_MAX_OUTPUT_TOKENS", "1024")),
}


def _api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


# ---------------------------------------------------------------------------
# LangGraph: State, nós e grafo
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    # add_messages faz o LangGraph ACRESCENTAR mensagens em vez de sobrescrever a lista
    messages: Annotated[list[BaseMessage], add_messages]


def _build_llm():
    api_key = _api_key()
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY no arquivo backend/.env para usar o agente.")

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
    )


def _no_agente(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Nó do LLM: decide se responde direto ou se chama alguma tool."""
    llm_com_tools = _build_llm().bind_tools(TOOLS)
    resposta = llm_com_tools.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
    return {"messages": [resposta]}


@lru_cache(maxsize=1)
def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agente", _no_agente)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agente")
    # se a última mensagem pedir uma tool vai para "tools", senão termina
    graph.add_conditional_edges("agente", tools_condition)
    graph.add_edge("tools", "agente")
    return graph.compile()


# ---------------------------------------------------------------------------
# Funções usadas pela camada HTTP (endpoint)
# ---------------------------------------------------------------------------
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


def _converter_historico(history: list[dict[str, str]]) -> list[BaseMessage]:
    mensagens: list[BaseMessage] = []
    for item in history[-8:]:  # só as últimas 8 mensagens
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

    resultado = _build_graph().invoke({"messages": mensagens}, config={"recursion_limit": 12})
    return _normalizar_conteudo(resultado["messages"][-1].content)


def status_agente() -> dict[str, Any]:
    return {
        "agent": "diogo_vieira_games",
        "responsibility": "Recomendar e explicar jogos a partir de um catálogo interno.",
        "llm_configured": bool(_api_key()),
        "model_config": MODEL_CONFIG,
        "tools": [t.name for t in TOOLS],
        "jogos_no_catalogo": len(CATALOGO),
    }