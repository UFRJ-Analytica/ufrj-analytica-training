from pathlib import Path

import os

import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


DOCUMENT_PATH = Path(__file__).parent / "financas_basicas.txt"

BACKEND_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(BACKEND_ENV_FILE)

COLLECTION_NAME = "julio_menescal_financas"

def carregar_documento() -> str:
    return DOCUMENT_PATH.read_text(encoding="utf-8")


def dividir_documento(texto: str) -> list[str]:
    chunks = [
        trecho.strip()
        for trecho in texto.split("\n\n\n")
        if trecho.strip()
    ]

    return chunks


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

def ingerir_documento():
    documento = carregar_documento()
    chunks = dividir_documento(documento)

    embeddings_model = criar_embeddings()

    vetores = embeddings_model.embed_documents(chunks)

    client = conectar_chroma()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    ids = [
        f"financas_basicas_{indice}"
        for indice in range(len(chunks))
    ]

    metadatas = [
        {
            "fonte": DOCUMENT_PATH.name,
            "chunk": indice,
        }
        for indice in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=vetores,
        metadatas=metadatas,
    )

    return collection, chunks

if __name__ == "__main__":
    collection, chunks = ingerir_documento()

    print(f"Documento: {DOCUMENT_PATH.name}")
    print(f"Chunks processados: {len(chunks)}")
    print(f"Collection: {collection.name}")
    print(f"Registros armazenados: {collection.count()}")