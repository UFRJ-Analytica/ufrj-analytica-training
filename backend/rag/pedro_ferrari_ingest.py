import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv("backend/.env")


BACKEND_DIR = Path(__file__).resolve().parents[1]

ARQUIVO = (
    BACKEND_DIR
    / "dados"
    / "pedro_ferrari_games.txt"
)

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


def carregar_documentos():
    texto = ARQUIVO.read_text(
        encoding="utf-8"
    )

    blocos = texto.split("\n---\n")

    documentos = []

    for bloco in blocos:
        bloco = bloco.strip()

        if bloco:
            documentos.append(bloco)

    return documentos


def criar_chunks(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = []
    metadados = []

    numero_documento = 0

    for documento in documentos:
        partes = splitter.split_text(
            documento
        )

        numero_chunk = 0

        for parte in partes:
            chunks.append(parte)

            metadata = {
                "source": ARQUIVO.name,
                "documento": numero_documento,
                "chunk": numero_chunk
            }

            metadados.append(metadata)

            numero_chunk += 1

        numero_documento += 1

    return chunks, metadados


def ingerir_documentos():
    documentos = carregar_documentos()

    chunks, metadados = criar_chunks(
        documentos
    )

    modelo_embeddings = criar_modelo_embeddings()

    print(
        f"Gerando embeddings para "
        f"{len(chunks)} chunks..."
    )

    vetores = modelo_embeddings.embed_documents(
        chunks
    )

    cliente = conectar_chroma()

    colecao = cliente.get_or_create_collection(
        name=NOME_COLECAO
    )

    ids = []

    for i in range(len(chunks)):
        ids.append(
            f"pedro_chunk_{i}"
        )

    colecao.upsert(
        ids=ids,
        documents=chunks,
        embeddings=vetores,
        metadatas=metadados
    )

    print(
        f"{len(chunks)} chunks armazenados "
        f"na coleção '{NOME_COLECAO}'."
    )


if __name__ == "__main__":
    ingerir_documentos()