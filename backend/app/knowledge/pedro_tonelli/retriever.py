"""
Retriever da base de conhecimento (RAG) do Agente de Analise de Dados.

Recebe uma pergunta, o proprio ChromaDB gera o embedding dela e devolve os
chunks mais proximos semanticamente (Top K), usando a colecao criada por
ingest.py.
"""
from __future__ import annotations

import os

import chromadb

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
COLLECTION_NAME = "pedro_tonelli_pandas_docs"


def buscar_contexto(pergunta: str, top_k: int = 3) -> list[dict[str, str]]:
    """Busca os `top_k` chunks mais relevantes pra pergunta."""
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    colecao = client.get_collection(COLLECTION_NAME)

    resultado = colecao.query(query_texts=[pergunta], n_results=top_k)

    chunks = []
    documentos = resultado["documents"][0]
    metadatas = resultado["metadatas"][0]
    distancias = resultado["distances"][0]

    for texto, meta, distancia in zip(documentos, metadatas, distancias):
        chunks.append(
            {
                "texto": texto,
                "fonte": meta["fonte"],
                "distancia": distancia,
            }
        )
    return chunks


if __name__ == "__main__":
    pergunta_teste = "como calcular a mediana de uma coluna?"
    print(f"Pergunta: {pergunta_teste}\n")
    for chunk in buscar_contexto(pergunta_teste):
        print(f"[{chunk['fonte']}] (distancia={chunk['distancia']:.4f})")
        print(chunk["texto"][:200])
        print()