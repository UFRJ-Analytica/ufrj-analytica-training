import os

import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv("backend/.env")


NOME_COLECAO = "pedro_ferrari_games"


def conectar_chroma():
    host = os.getenv(
        "CHROMA_HOST",
        "localhost"
    )

    port = int(
        os.getenv(
            "CHROMA_PORT",
            "8001"
        )
    )

    return chromadb.HttpClient(
        host=host,
        port=port
    )


def criar_modelo_embeddings():
    modelo = os.getenv(
        "PEDRO_FERRARI_EMBEDDING_MODEL",
        "models/gemini-embedding-001"
    )

    return GoogleGenerativeAIEmbeddings(
        model=modelo
    )


def recuperar_contexto(
    pergunta: str,
    quantidade: int = 3
) -> str:

    modelo_embeddings = criar_modelo_embeddings()

    vetor_pergunta = modelo_embeddings.embed_query(
        pergunta
    )

    cliente = conectar_chroma()

    colecao = cliente.get_collection(
        name=NOME_COLECAO
    )

    resultado = colecao.query(
        query_embeddings=[vetor_pergunta],
        n_results=quantidade,
        include=[
            "documents",
            "metadatas"
        ]
    )

    documentos = resultado["documents"][0]
    metadados = resultado["metadatas"][0]

    if len(documentos) == 0:
        return "Nenhuma informação encontrada na base."

    resposta = ""

    for i in range(len(documentos)):
        documento = documentos[i]
        metadata = metadados[i]

        resposta += documento
        resposta += "\n"
        resposta += "Fonte: "
        resposta += metadata["source"]
        resposta += "\n\n"

    return resposta