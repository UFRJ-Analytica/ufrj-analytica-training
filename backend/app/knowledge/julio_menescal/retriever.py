import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


BACKEND_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(BACKEND_ENV_FILE)

COLLECTION_NAME = "julio_menescal_financas"


def criar_embeddings():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nao configurada.")

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )


def conectar_chroma():
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8001"))

    return chromadb.HttpClient(
        host=host,
        port=port,
    )


def buscar_contexto(pergunta: str, quantidade: int = 3) -> list[dict]:
    embeddings = criar_embeddings()

    vetor_pergunta = embeddings.embed_query(pergunta)

    client = conectar_chroma()

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    resultado = collection.query(
        query_embeddings=[vetor_pergunta],
        n_results=quantidade,
    )

    documentos = resultado["documents"][0]
    metadatas = resultado["metadatas"][0]

    return [
        {
            "texto": documento,
            "metadata": metadata,
        }
        for documento, metadata in zip(documentos, metadatas)
    ]

if __name__ == "__main__":
    pergunta = "Por que meu dinheiro perde poder de compra com o tempo?"

    resultados = buscar_contexto(
        pergunta,
        quantidade=2,
    )

    for indice, resultado in enumerate(resultados, start=1):
        print(f"\n--- RESULTADO {indice} ---")
        print(resultado["texto"])
        print("Metadata:", resultado["metadata"])