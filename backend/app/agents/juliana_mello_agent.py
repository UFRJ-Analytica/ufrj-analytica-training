import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool

load_dotenv()  # lê o backend/.env

llm = ChatGoogleGenerativeAI(
    model=os.getenv("AGENTE_TESTE_MODEL", "gemini-3.6-flash"),
    google_api_key=os.getenv("GEMINI_API_KEY"),
   # temperature=0.3, # mais preciso >> serve de nada no gemini 3.6
    max_output_tokens=2048,
)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] # o state dele tem um campo único: messages
    # ele não substitui a lista inteira a cada atualização, mas adiciona novas mensagens à lista existente


# base de dados da tool
# tool = função python que o llm pode decidir chamar, mas toda função precisa fazer algo, precisando de uma fonte de informação p consultar e retornar
PERSONAGENS_STAR_WARS = {
    "luke skywalker": "Jedi, filho de Anakin Skywalker e Padmé Amidala, treinado por Obi-Wan Kenobi e Yoda.",
    "darth vader": "Antigo Jedi Anakin Skywalker, caiu para o Lado Sombrio e se tornou o braço direito do Imperador Palpatine.",
    "yoda": "Grão-Mestre Jedi, com mais de 900 anos, conhecido por sua sabedoria e forma de falar invertida.",
    "leia organa": "Princesa de Alderaan, líder da Rebelião e irmã gêmea de Luke Skywalker.",
    "han solo": "Contrabandista, capitão da nave Millennium Falcon, parceiro de Chewbacca.",
    "obi-wan kenobi": "Mestre Jedi que treinou Anakin e Luke Skywalker, conhecido por sua sabedoria e habilidades com o sabre de luz.",
}

# quando usuario perguntar sobre um personagem específico, o LLM vai chamar a tool buscar_personagem, que vai consultar a base de dados acima e retornar a resposta correta

@tool
def buscar_personagem(nome: str) -> str:
    """Busca informações sobre um personagem específico do universo Star Wars,
    como 'Luke Skywalker', 'Darth Vader' ou 'Yoda'."""
    nome_normalizado = nome.lower().strip()
    if nome_normalizado in PERSONAGENS_STAR_WARS:
        return PERSONAGENS_STAR_WARS[nome_normalizado]
    return f"Não tenho informações salvas sobre '{nome}'. Personagens disponíveis: {', '.join(PERSONAGENS_STAR_WARS.keys())}"

# quando nao tem esse "dicionário", a LLM pode não ser tão confiável, podendo preencher lacunas de conhecimento com "alucinações"
# daria pra conectar a um banco de dados externo, mas por enquanto deixarei mais simples
# daria tbm pra fazer ele pesquisar na internet (geral, não direcionada a um endereço espeífico, como seria com o banco de dados), mas isso é mais complexo e não é o objetivo do treinamento


# system prompt da parte 1
'''
SYSTEM_PROMPT = SystemMessage(content=(
    "Você é um assistente especializado no universo Star Wars. Converse com "
    "o usuário sobre filmes, personagens, facções e história da saga de forma "
    "envolvente e precisa. Quando o usuário perguntar sobre um personagem "
    "específico, use a ferramenta buscar_personagem para checar os dados "
    "antes de responder, em vez de confiar só na sua memória. "
    "Responda de forma direta e objetiva, focada exclusivamente no que foi "
    "perguntado sobre o universo Star Wars. Não faça analogias, comparações "
    "ou conexões com outros assuntos que não tenham sido mencionados pelo "
    "usuário, mesmo que veja alguma semelhança temática. "
    "Se não souber algo com certeza, diga que não sabe em vez de inventar."
))
'''

# system prompt da parte 3
SYSTEM_PROMPT = SystemMessage(content=(
    "Você é um assistente especializado no universo Star Wars. "
    "Se o usuário perguntar sobre a biografia básica de personagens como Luke ou Vader, use a ferramenta 'buscar_personagem'. "
    "Se o usuário perguntar sobre história, lore, planetas ou conceitos (como A Força), OBRIGATORIAMENTE use a ferramenta 'consultar_arquivos_jedi' para buscar informações no banco de dados antes de responder. "
    "Baseie sua resposta EXCLUSIVAMENTE nos dados recuperados pela tool utilizada. Não invente informações ausentes no contexto. "
    "Responda de forma direta e objetiva, focada exclusivamente no que foi perguntado sobre o universo Star Wars. "
    "Não faça analogias, comparações ou conexões com outros assuntos — como arquitetura de software, tecnologia ou o próprio processo de desenvolvimento deste agente — mesmo que veja alguma semelhança temática nas palavras da pergunta."
))

# pro entregável 3:
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool


# Cria a conexão com o banco para leitura
chroma_client = chromadb.HttpClient(host="localhost", port=8001)
colecao = chroma_client.get_collection(name="star_wars_docs")
embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

@tool
def consultar_arquivos_jedi(pergunta: str) -> str:
    """busca informações de contexto nos arquivos (arquivos .txt ingeridos) sobre 
    a história, lore, planetas e conceitos gerais do universo star wars."""
    
    # transforma a pergunta do usuário em embedding
    vetor_pergunta = embedder.embed_query(pergunta)
    
    # faz a busca semântica no banco vetorial (trazendo os 3 chunks mais parecidos)
    resultados = colecao.query(
        query_embeddings=[vetor_pergunta],
        n_results=3
    )
    
    # verifica se encontrou algo
    documentos_encontrados = resultados.get("documents", [[]])[0]
    if not documentos_encontrados:
        return "Nenhuma informação relevante encontrada nos arquivos do Templo Jedi."
    
    # junta os chunks para o LLM usar como contexto
    contexto = "\n\n".join(documentos_encontrados)
    return f"Contexto recuperado dos documentos:\n{contexto}"

tools = [buscar_personagem, consultar_arquivos_jedi]
llm_com_tools = llm.bind_tools(tools)

def chamar_llm(state: AgentState) -> AgentState:
    mensagens = [SYSTEM_PROMPT] + state["messages"]
    resposta = llm_com_tools.invoke(mensagens)
    return {"messages": [resposta]}


# construir o grafo de estados do agente:
grafo = StateGraph(AgentState) #cria grafo vazio do tipo que vai carregar um AgentState (dicionario com mensagens definido antes), não tem nó nem seta ainda!

# ir add os nós e setas:
grafo.add_node("agente", chamar_llm)
grafo.add_node("tools", ToolNode(tools)) 

grafo.set_entry_point("agente")  # execução começa pelo nó "agente"
grafo.add_conditional_edges("agente", tools_condition) # bifurcação! depois de chamar o agente, vê se ele precisa chamar a tool ou não! é onde existe decisão
grafo.add_edge("tools", "agente") # seta que "volta"(de tool pra agente), pois o LLM precisa pegar o resultado e transformar em uma resposta pro usuário

agent_graph = grafo.compile()

# a resposta tava ficando muito feia por conta do mensagem.content mais recente
# essa função faz extrair só o texto da resposta
def extrair_texto_resposta(mensagem) -> str:
    """Extrai o texto puro de uma mensagem do LLM, independente do formato
    (string simples ou lista de blocos de conteúdo)."""
    conteudo = mensagem.content
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        partes = [
            bloco["text"]
            for bloco in conteudo
            if isinstance(bloco, dict) and bloco.get("type") == "text"
        ]
        return "\n".join(partes)
    return str(conteudo)

# o LLM responde mais do que está no meu dicionário! perguntei pro claude e hei a explicação:
'''
Ótima observação — isso é exatamente a continuação daquela conversa sobre "de onde vem o conhecimento" que tivemos antes. Vamos destrinchar o que está acontecendo aqui.

O que realmente aconteceu no fluxo

Você perguntou "Quem é o Han Solo?"
O agente decidiu chamar buscar_personagem
A tool devolveu só o que está no seu dicionário — algo como "Han Solo: Contrabandista, capitão da nave Millennium Falcon, parceiro de Chewbacca." (uma frase curta)
O fluxo voltou pro agente, que recebeu esse resultado da tool e formulou a resposta final

O ponto-chave está no passo 4: quando o LLM monta a resposta final, ele não fica limitado ao que a tool devolveu. Ele tem acesso a dois "conhecimentos" ao mesmo tempo:

O que a tool acabou de retornar (o dado "confiável", vindo da sua fonte)
Todo o conhecimento paramétrico dele sobre Star Wars (que, como já vimos, é bastante extenso, porque é uma franquia super documentada)

Sem uma instrução explícita dizendo "não faça isso", o modelo naturalmente combina os dois pra dar uma resposta mais completa e "conversacional" — daí vem o romance com a Leia, a liderança na Aliança Rebelde, etc. Provavelmente está tudo factualmente certo (é conhecimento bem sólido sobre a franquia), mas não veio da sua tool.

A Google pré-treina, ou seja, treina o modelo (que eu estou alugando acesso e que foi deixado pronto através da API) antes de disponibilizar a API, com uma grande quantidade de dados públicos, incluindo informações sobre Star Wars. Então, mesmo que a tool só devolva uma frase curta, o modelo "lembra" de outros detalhes e os inclui na resposta final.
'''

# .venv\Scripts\python -m uvicorn backend.app.main:app --reload --reload-dir backend

# python -m backend.app.juliana_mello.rag.ingestao --> ja que mudei a localização

# streamlit run pages/nome_sobrenome_chat.py