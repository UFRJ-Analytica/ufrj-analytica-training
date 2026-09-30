"""
Pipeline de ingestao para a base de conhecimento (RAG) do Agente de Analise
de Dados.

Fonte dos documentos: docstrings oficiais das funcoes do pandas instalado
no ambiente (pandas.__version__). Isso garante que a base seja gerada
sempre a partir da mesma fonte, sem depender de arquivos externos.

Pipeline: Document Loader -> Text Splitting -> Chunks -> Embedding (feito
pelo proprio ChromaDB, com o embedding padrao) -> Vetores -> ChromaDB.

Uso:
    .venv\\Scripts\\python.exe backend\\app\\knowledge\\pedro_tonelli\\ingest.py
"""
from __future__ import annotations

import inspect
import os

import chromadb
import pandas as pd

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
COLLECTION_NAME = "pedro_tonelli_pandas_docs"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

# --- Document Loader ------------------------------------------------------
# Carrega a documentacao direto das docstrings do pandas instalado.
FUNCOES_DOCUMENTADAS = {
    "pandas.Series.mean": pd.Series.mean,
    "pandas.Series.median": pd.Series.median,
    "pandas.Series.std": pd.Series.std,
    "pandas.Series.quantile": pd.Series.quantile,
    "pandas.DataFrame.describe": pd.DataFrame.describe,
    "pandas.DataFrame.groupby": pd.DataFrame.groupby,
    "pandas.DataFrame.corr": pd.DataFrame.corr,
    "pandas.DataFrame.merge": pd.DataFrame.merge,
}


def carregar_documentos() -> list[dict[str, str]]:
    """Cada documento e a docstring completa de uma funcao do pandas."""
    documentos = []
    for nome, funcao in FUNCOES_DOCUMENTADAS.items():
        texto = inspect.getdoc(funcao)
        if not texto:
            continue
        documentos.append({"fonte": nome, "texto": texto})
    return documentos


# --- Text Splitting ---------------------------------------------------------
def dividir_em_chunks(
    texto: str, tamanho: int = CHUNK_SIZE, sobreposicao: int = CHUNK_OVERLAP
) -> list[str]:
    """
    Divide o texto em pedacos de ate `tamanho` caracteres, tentando cortar
    em paragrafos (linha em branco) antes de cortar no meio de uma frase.
    """
    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]

    chunks: list[str] = []
    atual = ""

    for paragrafo in paragrafos:
        if len(atual) + len(paragrafo) + 1 <= tamanho:
            atual = f"{atual}\n{paragrafo}".strip()
            continue

        if atual:
            chunks.append(atual)

        if len(paragrafo) <= tamanho:
            atual = paragrafo
        else:
            for inicio in range(0, len(paragrafo), tamanho - sobreposicao):
                chunks.append(paragrafo[inicio : inicio + tamanho])
            atual = ""

    if atual:
        chunks.append(atual)

    return chunks


def montar_chunks(documentos: list[dict[str, str]]) -> list[dict[str, str]]:
    resultado = []
    for doc in documentos:
        pedacos = dividir_em_chunks(doc["texto"])
        for indice, pedaco in enumerate(pedacos):
            resultado.append(
                {
                    "id": f"{doc['fonte']}::{indice}",
                    "texto": pedaco,
                    "fonte": doc["fonte"],
                    "indice_chunk": indice,
                }
            )
    return resultado


# --- Embedding + armazenamento no ChromaDB -----------------------------------
def ingerir() -> None:
    documentos = carregar_documentos()
    chunks = montar_chunks(documentos)

    print(f"pandas versao: {pd.__version__}")
    print(f"Documentos carregados: {len(documentos)}")
    print(f"Chunks gerados: {len(chunks)}")

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    colecao = client.create_collection(name=COLLECTION_NAME)

    colecao.add(
        ids=[c["id"] for c in chunks],
        documents=[c["texto"] for c in chunks],
        metadatas=[
            {"fonte": c["fonte"], "indice_chunk": c["indice_chunk"]} for c in chunks
        ],
    )

    print(f"Colecao '{COLLECTION_NAME}' populada com {colecao.count()} chunks.")


if __name__ == "__main__":
    ingerir()