from __future__ import annotations
import json
import os
import statistics
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from dotenv import load_dotenv


BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(BACKEND_ENV_FILE)


SYSTEM_PROMPT = """
Voce e um agente criado para auxiliar em analise de dados.

Responsabilidade:
- auxiliar na interpretacao e analise de conjuntos de dados numericos;
- realizar calculos estatisticos e explicar seu significado;
- orientar sobre boas praticas de analise com Python e Pandas;
- responder em portugues, com linguagem tecnica mas acessivel.

Regras:
- utilize os resultados das tools para embasar sua resposta;
- quando receber numeros do usuario, aplique os calculos estatisticos disponíveis;
- explique o que cada metrica significa no contexto da analise;
- indique limitacoes dos dados quando relevante (ex: amostra pequena, outliers);
- nao invente dados que o usuario nao forneceu;
- se faltar contexto, pergunte o que o usuario quer analisar;
- responda apenas o que for perguntado.
""".strip()

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": "gemini-3.8-flash",
    "temperature": 0.4,
    "max_output_tokens": 1024
}


def _extrair_numeros(mensagem: str) -> list[float]:
    """Tenta extrair uma lista de numeros de uma mensagem de texto."""
    import re

    tokens = re.findall(r"-?\d+(?:[.,]\d+)?", mensagem)
    numeros: list[float] = []
    for t in tokens:
        try:
            numeros.append(float(t.replace(",", ".")))
        except ValueError:
            pass
    return numeros


def _calcular_media_impl(valores: list[float]) -> dict[str, Any]:
    if not valores:
        return {"erro": "Nenhum valor numerico encontrado para calcular a media."}
    media = sum(valores) / len(valores)
    return {
        "operacao": "media",
        "valores": valores,
        "n": len(valores),
        "resultado": round(media, 4),
    }


def _calcular_mediana_impl(valores: list[float]) -> dict[str, Any]:
    if not valores:
        return {"erro": "Nenhum valor numerico encontrado para calcular a mediana."}
    mediana = statistics.median(valores)
    return {
        "operacao": "mediana",
        "valores": sorted(valores),
        "n": len(valores),
        "resultado": round(mediana, 4),
    }


def _calcular_estatisticas_impl(valores: list[float]) -> dict[str, Any]:
    if not valores:
        return {"erro": "Nenhum valor numerico encontrado para calcular estatisticas."}
    if len(valores) == 1:
        return {
            "operacao": "estatisticas",
            "valores": valores,
            "n": 1,
            "media": valores[0],
            "mediana": valores[0],
            "minimo": valores[0],
            "maximo": valores[0],
            "amplitude": 0,
            "desvio_padrao": None,
            "aviso": "Apenas um valor fornecido; desvio padrao nao calculavel.",
        }

    media = sum(valores) / len(valores)
    mediana = statistics.median(valores)
    desvio = statistics.stdev(valores)
    minimo = min(valores)
    maximo = max(valores)
    amplitude = maximo - minimo

    return {
        "operacao": "estatisticas",
        "valores": valores,
        "n": len(valores),
        "media": round(media, 4),
        "mediana": round(mediana, 4),
        "minimo": round(minimo, 4),
        "maximo": round(maximo, 4),
        "amplitude": round(amplitude, 4),
        "desvio_padrao": round(desvio, 4),
    }


@tool
def calcular_media(mensagem: str) -> str:
    """Extrai numeros da mensagem do usuario e calcula a media aritmetica."""
    valores = _extrair_numeros(mensagem)
    return json.dumps(_calcular_media_impl(valores), ensure_ascii=False)

@tool
def calcular_mediana(mensagem: str) -> str:
    """Extrai numeros da mensagem do usuario e calcula a mediana."""
    valores = _extrair_numeros(mensagem)
    return json.dumps(_calcular_mediana_impl(valores), ensure_ascii=False)

@tool
def calcular_estatisticas(mensagem: str) -> str:
    """Extrai numeros da mensagem e retorna estatisticas descritivas completas:
    media, mediana, minimo, maximo, amplitude e desvio padrao."""
    valores = _extrair_numeros(mensagem)
    return json.dumps(_calcular_estatisticas_impl(valores), ensure_ascii=False)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    tool_context: str


def _executar_tool_estatisticas(mensagem: str) -> str:
    """Executa calcular_estatisticas e retorna o JSON como string."""
    fn = calcular_estatisticas
    if hasattr(fn, "invoke"):
        return fn.invoke({"mensagem": mensagem})
    return fn(mensagem)


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
    api_key = os.getenv("GEMINI_API_KEY")

    return ChatGoogleGenerativeAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_output_tokens=MODEL_CONFIG["max_output_tokens"],
        google_api_key=api_key,
    )


def _node_tool_context(state: "AgentState") -> dict[str, str]:
    mensagem = _ultima_mensagem_usuario(state["messages"])
    resultado = _executar_tool_estatisticas(mensagem)
    return {"tool_context": resultado}


def _node_llm(state: "AgentState") -> dict[str, list[Any]]:
    prompt_com_contexto = (
        f"{SYSTEM_PROMPT}\n\n"
        "Resultado produzido pela tool calcular_estatisticas com os dados da mensagem:\n"
        f"{state.get('tool_context', '')}\n\n"
        "Use esses resultados na sua resposta quando forem relevantes. "
        "Se nenhum numero foi encontrado, responda normalmente sem mencionar o calculo."
    )

    resposta = _build_llm().invoke(
        [SystemMessage(content=prompt_com_contexto), *state["messages"]]
    )
    return {"messages": [resposta]}


@lru_cache(maxsize=1)
def _build_graph():

    graph = StateGraph(AgentState)
    graph.add_node("calcular_contexto", _node_tool_context)
    graph.add_node("gerar_resposta", _node_llm)
    graph.add_edge(START, "calcular_contexto")
    graph.add_edge("calcular_contexto", "gerar_resposta")
    graph.add_edge("gerar_resposta", END)
    return graph.compile()


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
        raise ValueError("A mensagem nao pode estar vazia.")


    mensagens = _converter_historico(history or [])
    mensagens.append(HumanMessage(content=mensagem))

    result = _build_graph().invoke({"messages": mensagens, "tool_context": ""})
    resposta = result["messages"][-1]
    return _normalizar_conteudo(resposta.content)
