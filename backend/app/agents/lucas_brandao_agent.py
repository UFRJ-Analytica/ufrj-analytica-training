import os
from typing import Annotated, TypedDict
import chromadb
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

#Ingestão de Dados e Base de Conhecimento (RAG)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BACKEND_DIR, "../../../data/copa_2030_info.txt")

#Conecta ao ChromaDB no Docker
chroma_client = chromadb.HttpClient(host="127.0.0.1", port=8001)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#Função para garantir que o banco recebe os dados
def base_copa_v2():
    try:
        colecao_existe = any(c.name == "base_copa_v2" for c in chroma_client.list_collections())
        
        if not colecao_existe:
            print("Injetando dados no ChromaDB...")
            loader = TextLoader(FILE_PATH, encoding="utf-8")
            documentos = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
            chunks = text_splitter.split_documents(documentos)
            
            vector_store = Chroma(client=chroma_client, collection_name="base_copa_v2", embedding_function=embeddings)
            vector_store.add_documents(chunks)
            print("Conhecimento injetado!")
            return vector_store
        else:
            return Chroma(client=chroma_client, collection_name="base_copa_v2", embedding_function=embeddings)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a base de dados. Erro: {e}")
        return None

vector_store = base_copa_v2()


#1. Definição do Estado do Grafo
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    contexto: str # Nova variável de estado para armazenar o contexto recuperado

#2. Tools (Ferramentas de Logística e Orçamento)
@tool
def estimar_orcamento_copa(dias: int, nivel_conforto: str = "medio") -> str:
    """Calcula uma estimativa de orçamento para a Copa 2030."""
    custo_base = {"mochileiro": 80, "medio": 200, "luxo": 500}
    custo_diario = custo_base.get(nivel_conforto.lower(), 200)
    return f"Orçamento estimado para {dias} dias: € {custo_diario * dias:.2f}."

@tool
def pesquisar_base_conhecimento(pergunta: str) -> str:
    """Ferramenta que o agente usa para pesquisar regras de visto ou transporte nos documentos RAG."""
    if vector_store is None:
        return "Base de dados indisponível."
    docs = vector_store.similarity_search(pergunta, k=2)
    textos_recuperados = [doc.page_content for doc in docs]
    return "INFORMAÇÃO RECUPERADA DOS DOCUMENTOS: " + " | ".join(textos_recuperados)

tools = [estimar_orcamento_copa, pesquisar_base_conhecimento]

#3. Configuração do Modelo e Prompt
SYSTEM_PROMPT = """Você é um planejador de viagens especialista na Copa do Mundo FIFA de 2030.
Sempre que o usuário perguntar sobre VISTOS ou FERRY BOAT, você DEVE, obrigatoriamente, usar a ferramenta 'pesquisar_base_conhecimento' para ler os documentos oficiais antes de responder. Nunca invente dados logísticos que não estejam na base."""

def build_llm():
    llm = ChatGoogleGenerativeAI(model=os.getenv("AGENTE_TESTE_MODEL", "gemini-3.6-flash"), temperature=0.2)
    return llm.bind_tools(tools)

#4. Construção dos Nós e do Grafo
def call_model(state: AgentState):
    messages = state['messages']
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    llm_with_tools = build_llm()
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "tools"
    return END

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    return workflow.compile()

app_agent = build_graph()

#5. Função de Entrada para o FastAPI
def chat_com_agente(mensagem_usuario: str, history: list = None):
    inputs = {"messages": [HumanMessage(content=mensagem_usuario)]}
    result = app_agent.invoke(inputs)
    return result["messages"][-1].content