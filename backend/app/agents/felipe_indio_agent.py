import os
import chromadb
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
chroma_client = chromadb.HttpClient(host="localhost", port=8001)
vectorstore = Chroma(
    client=chroma_client, 
    collection_name="base_filmes", 
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

@tool
def buscar_info_filmes(query: str) -> str:
    """Use esta ferramenta para buscar sinopses e informações sobre filmes na base de dados."""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

tools = [buscar_info_filmes]

model_name = os.getenv("AGENTE_TESTE_MODEL", "gemini-2.5-flash")
llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[buscar_info_filmes])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

agent_graph = graph_builder.compile()