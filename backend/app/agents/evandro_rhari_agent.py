from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

import os
import getpass
from dotenv import load_dotenv
from pathlib import Path
from typing import Annotated
from functools import lru_cache



# -- Enviroment Setup -- #

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

try:
    load_dotenv(BACKEND_ENV_FILE)
except ImportError:
    print("Erro ao carregar .env")
    exit()

if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")


# -- Model Setup -- #

MODEL_CONFIG = {
    "provider": "google_genai",
    "model": os.getenv("AGENTE_MODEL", "gemini-3.7-flash"),
    "temperature": float(os.getenv("AGENTE_TEMPERATURE", "0.2")),
    "max_output_tokens": int(os.getenv("AGENTE_MAX_OUTPUT_TOKENS", "1024")),
    "api_key": os.getenv("GEMINI_API_KEY")
}

CONTEXT_PROMPT = "You are a bratty and cute anime tsundere that's helping the user learn french. Translate to french the user sentence" \
                 "Do not use emoticon or make explicit anime references, just adopt the persona. " 


def _build_llm(model_config : dict):
    """Builds the LLM according to the model config."""

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY ou GOOGLE_API_KEY para usar o LLM.")

    return ChatGoogleGenerativeAI(
        model=model_config["model"],
        temperature=model_config["temperature"],
        max_output_tokens=model_config["max_output_tokens"],
        google_api_key=model_config["api_key"],
    )


# -- Chat Tools -- #

def _generate_response(state: AgentState):
    """Node action for generating a response based on the previous interactions
        and current message stored in the AgentState context propreties. 
    """
    messages =  [
                    SystemMessage(content=CONTEXT_PROMPT), 
                    HumanMessage(content=state.get("current_message", 'Hello!'))
                ]

    model = _build_llm(MODEL_CONFIG)
    response = model.invoke(messages)
    ai_msg = response.content[0]['text']
    return {"messages": [ai_msg], "current_message": ai_msg}


# -- Graph Steup -- #

class AgentState():
    """Denotes the structure to be shared in and manipulated by the graph's nodes"""
    messages : Annotated[list[BaseMessage], add_messages] # List of the previous messages. LangGraph updates it automatically using 'add_message'
    current_message : str                                 # Curent context. Just saves the current message.


@lru_cache(maxsize=1)
def _build_graph():
    """Creates the action nodes using the functions preceeded by _ and connects 
    them by edges. As not to recompile the graph everytime, this functions returns
    is cached.
    """

    graph = StateGraph(AgentState)

    graph.add_node("generate_response", _generate_response)

    graph.add_edge(START, "generate_response")
    graph.add_edge("generate_response", END)
    return graph.compile()


# -- Chating Endpoint -- #

def chat(human_message):
    """Answers the human message. This function will be used for the endpoint."""
    result = _build_graph().invoke({"messages": [], "current_message": human_message})
    ai_msg = result["messages"][-1].content
    return ai_msg



ai_msg = chat("So, can you translate 'Gemini is best girl' to French? Pretty please!")
print(ai_msg)