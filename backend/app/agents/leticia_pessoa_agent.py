
import os
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

import requests

# Carrega as variáveis de ambiente de backend/.env
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


# SYSTEM PROMPT
SYSTEM_PROMPT = """
Você é um agente especializado em indicadores demográficos.

Sua responsabilidade é:
- auxiliar na interpretação de indicadores populacionais;
- consultar dados demográficos utilizando as ferramentas disponíveis;
- comparar municípios, estados e regiões;
- explicar comparações entre valores e períodos;
- realizar cálculos quando necessário;
- responder de forma clara, objetiva e didática.

Você possui uma ferramenta chamada consultar_indicadores_api.

Use essa ferramenta sempre que a pergunta depender de dados populacionais
da aplicação.

Os tipos de consulta disponíveis são:

- municipio:
  use quando a pergunta for sobre um município específico.
  Informe o nome do município no parâmetro termo.

- estados:
  use para perguntas sobre população dos estados,
  comparação entre estados ou identificação do estado mais populoso.

- regioes:
  use para perguntas sobre população das regiões brasileiras
  ou comparação entre regiões.

- resumo:
  use para perguntas sobre população total,
  quantidade de municípios, quantidade de estados,
  ano de referência ou município mais populoso.

Regras:
- não invente dados;
- não responda perguntas sobre os dados da aplicação apenas com seu
  conhecimento interno;
- sempre utilize a ferramenta quando a resposta depender dos dados
  populacionais disponíveis na API;
- após receber os dados da ferramenta, analise-os para responder
  exatamente à pergunta do usuário;
- quando realizar cálculos, explique brevemente o resultado;
- quando não houver informações suficientes, informe ao usuário.
""".strip()


# Configuração do modelo
MODEL_CONFIG = {
    "model": os.getenv(
        "LETICIA_PESSOA_MODEL",
        "openai/gpt-4o-mini",
    ),
    "temperature": 0.2,
    "max_output_tokens": 1024,
}


# STATE
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# TOOL
@tool
def calcular_variacao_percentual(
    valor_inicial: float,
    valor_final: float,
) -> str:
    """Calcula a variação percentual entre um valor inicial e um valor final."""

    if valor_inicial == 0:
        return "Não é possível calcular variação percentual com valor inicial igual a zero."

    variacao = ((valor_final - valor_inicial) / valor_inicial) * 100

    return f"A variação percentual foi de {variacao:.2f}%."

@tool
def consultar_indicadores_api(tipo_consulta: str, termo: str | None = None) -> str:
    """
    Consulta indicadores demográficos na API.

    Tipos de consulta disponíveis:
    - municipio
    - estados
    - regioes
    - resumo
    """

    base_url = os.getenv(
        "LETICIA_DATA_API_URL",
        "http://127.0.0.1:8000",
    )

    endpoints = {
        "municipio": "/leticia-pessoa/populacao/municipio",
        "estados": "/leticia-pessoa/populacao/por-uf",
        "regioes": "/leticia-pessoa/populacao/por-regiao",
        "resumo": "/leticia-pessoa/estatisticas/resumo",
    }

    caminho = endpoints.get(tipo_consulta)

    if not caminho:
        return (
            "Tipo de consulta inválido. "
            "Use: municipio, estados, regioes ou resumo."
        )

    try:
        response = requests.get(
            f"{base_url}{caminho}",
            timeout=10,
        )

        response.raise_for_status()
        dados = response.json()

        if tipo_consulta == "municipio":
            if not termo:
                return "Informe o nome do município."

            for item in dados:
                if item["nome_municipio"].lower() == termo.lower():
                    return (
                        f"{item['nome_municipio']} possui "
                        f"{item['populacao']} habitantes."
                    )

            return f"Município '{termo}' não encontrado."

        return str(dados)

    except requests.RequestException as exc:
        return f"Erro ao consultar a API: {exc}"
# Lista de ferramentas disponíveis para o agente
TOOLS = [
    calcular_variacao_percentual,
    consultar_indicadores_api,
    ]


def criar_modelo():
    """Cria o LLM via OpenRouter e disponibiliza as tools para ele."""

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY não encontrada. Configure a chave em backend/.env."
        )

    modelo = ChatOpenAI(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        max_tokens=MODEL_CONFIG["max_output_tokens"],
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    return modelo.bind_tools(TOOLS)


def node_agente(state: AgentState):
    """Nó responsável por enviar o estado atual para o LLM."""

    modelo = criar_modelo()

    resposta = modelo.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]
    )

    return {"messages": [resposta]}


def criar_grafo():
    """Monta e compila o fluxo do agente."""

    graph = StateGraph(AgentState)

    # Nós
    graph.add_node("agente", node_agente)
    graph.add_node("tools", ToolNode(TOOLS))

    # Entrada
    graph.add_edge(START, "agente")

    # O próprio resultado do LLM determina se uma tool deve ser executada
    graph.add_conditional_edges(
        "agente",
        tools_condition,
    )

    # Depois da tool, voltamos ao agente
    graph.add_edge("tools", "agente")

    return graph.compile()


def responder(message: str) -> str:
    """Função pública utilizada posteriormente pelo FastAPI."""

    if not message.strip():
        raise ValueError("A mensagem não pode estar vazia.")

    agente = criar_grafo()

    resultado = agente.invoke(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        }
    )

    return resultado["messages"][-1].content