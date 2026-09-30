"""
Retrieval do agente de Python (Isaac Vianna).

Conecta no ChromaDB (via HttpClient), expoe um retriever pronto para o
LangGraph usar e traz uma demo de busca semantica pela linha de comando:

    .venv\\Scripts\\python -m backend.app.rag.isaac_vianna_retriever "pergunta"

Nada aqui conecta no Chroma no momento do import: a conexao so acontece
na primeira chamada de get_vectorstore() (cache via lru_cache), para o
backend continuar subindo mesmo com o Chroma desligado.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND_ENV_FILE)
except ImportError:
    pass

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ---------------------------------------------------------------------------
# Configuracao (lida do backend/.env; ver README/tarefa para a lista completa)
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = os.getenv("ISAAC_VIANNA_EMBEDDING_MODEL", "models/gemini-embedding-001")
COLLECTION_NAME = os.getenv("ISAAC_VIANNA_COLLECTION", "isaac_vianna_python")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))


def _build_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Cria a funcao de embeddings usando a mesma API key do agente."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY para gerar embeddings.")
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=api_key)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    """Cria (uma unica vez, de forma preguicosa) a conexao com o ChromaDB."""
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=_build_embeddings(),
    )


def get_retriever(k: int = 4):
    """Retorna um retriever LangChain que busca os `k` chunks mais relevantes."""
    return get_vectorstore().as_retriever(search_kwargs={"k": k})


def format_docs(docs: list[Document]) -> str:
    """Formata os documentos recuperados como contexto para o system prompt."""
    blocos = [f"[Fonte: {doc.metadata.get('source', 'desconhecida')}]\n{doc.page_content}" for doc in docs]
    return "\n\n".join(blocos)


def _demo_busca_semantica(pergunta: str, k: int = 4) -> None:
    """Roda uma busca semantica e imprime os top K resultados com score."""
    resultados = get_vectorstore().similarity_search_with_score(pergunta, k=k)

    print(f"Pergunta: {pergunta}\n")
    for posicao, (doc, score) in enumerate(resultados, start=1):
        fonte = doc.metadata.get("source", "desconhecida")
        trecho = doc.page_content[:200].replace("\n", " ")
        print(f"{posicao}. source={fonte} score={score:.4f}")
        print(f"   {trecho}...\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Uso: python -m backend.app.rag.isaac_vianna_retriever "pergunta"')
        sys.exit(1)

    _demo_busca_semantica(sys.argv[1])
