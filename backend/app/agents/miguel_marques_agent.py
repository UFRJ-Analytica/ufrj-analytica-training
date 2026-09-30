import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Lê o backend/.env (este arquivo está em backend/app/agents/, então subimos 2 pastas)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# 1) SYSTEM PROMPT: quem é o agente e como deve responder
SYSTEM_PROMPT = """Você é o Agente Docker, assistente especializado em Docker,
Dockerfile e Docker Compose. Responda sempre em português do Brasil, de forma clara,
objetiva e didática. Se a pergunta não for sobre Docker, diga educadamente que
só responde sobre esse assunto. Se não souber algo, diga que não sabe; não invente.
Quando o usuário perguntar sobre um comando Docker específico, use a ferramenta
buscar_comando e baseie a resposta no resultado dela."""


# 2) STATE: o "caderno" do agente (add_messages acrescenta em vez de sobrescrever)
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# 3) FERRAMENTA: função comum que o modelo pode pedir para executar
COMANDOS = {
    "build": "docker build -t <nome> .  -> cria uma imagem a partir do Dockerfile da pasta atual.",
    "run": "docker run -d -p <host>:<container> --name <nome> <imagem>  -> cria e inicia um container.",
    "ps": "docker ps  -> lista os containers ativos (com -a, inclui os parados).",
    "logs": "docker logs <container>  -> mostra a saída do container (com -f, acompanha ao vivo).",
    "stop": "docker stop <container>  -> para o container.",
    "rm": "docker rm -f <container>  -> remove o container.",
    "images": "docker images  -> lista as imagens locais.",
    "compose up": "docker compose up --build  -> reconstrói e sobe todos os serviços do compose.yaml.",
    "compose down": "docker compose down  -> para e remove containers e rede (os volumes são mantidos).",
    "compose ps": "docker compose ps  -> mostra o estado dos serviços do Compose.",
}


@tool
def buscar_comando(comando: str) -> str:
    """Retorna a sintaxe e a explicação de um comando Docker.
    Use quando o usuário perguntar como usar um comando (ex.: build, run, ps, logs, compose up)."""
    termo = comando.lower().replace("docker", "").strip()
    achados = [descricao for nome, descricao in COMANDOS.items() if termo and termo in nome]
    if not achados:
        return f"Comando '{comando}' não encontrado. Disponíveis: {', '.join(COMANDOS)}."
    return "\n".join(achados)


TOOLS = [buscar_comando]


# 4) MODELO: criado uma única vez (cache) e só quando for usado
@lru_cache(maxsize=1)
def _modelo() -> ChatOpenAI:
    chave = os.getenv("OPENROUTER_API_KEY")
    nome = os.getenv("OPENROUTER_MODEL")
    # Validação: diz exatamente o que falta no backend/.env
    faltando = [n for n, v in (("OPENROUTER_API_KEY", chave), ("OPENROUTER_MODEL", nome)) if not v]
    if faltando:
        raise RuntimeError(f"Variáveis ausentes em backend/.env: {', '.join(faltando)}")
    return ChatOpenAI(
        model=nome,
        api_key=chave,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,     # baixo = respostas mais estáveis e técnicas
        max_completion_tokens=2048,     # limite do tamanho da resposta
        max_retries=5,       # repete em erros temporários (como o 429)
        timeout=60,          # desiste de uma tentativa após 60 segundos
    )


# 5) NÓ DO AGENTE: chama o modelo, que conhece as ferramentas via bind_tools
def no_agente(state: AgentState) -> dict:
    resposta = _modelo().bind_tools(TOOLS).invoke(
        [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    )
    return {"messages": [resposta]}


# 6) GRAFO: ciclo agente <-> ferramentas
_g = StateGraph(AgentState)
_g.add_node("agente", no_agente)
_g.add_node("tools", ToolNode(TOOLS))
_g.add_edge(START, "agente")
_g.add_conditional_edges("agente", tools_condition)   # pediu tool? vai p/ "tools", senão termina
_g.add_edge("tools", "agente")                        # resultado da tool volta ao modelo
grafo = _g.compile()


# 7) Converte o conteúdo da resposta em texto (pode vir como str ou lista de blocos)
def _texto(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo.strip()
    return "".join(
        b.get("text", "") if isinstance(b, dict) else str(b) for b in conteudo
    ).strip()


# 8) FUNÇÃO DE ENTRADA: o que o endpoint vai chamar
def executar_agente(mensagem: str) -> str:
    resultado = grafo.invoke({"messages": [HumanMessage(content=mensagem)]})
    return _texto(resultado["messages"][-1].content) or "O modelo não retornou texto. Tente novamente."