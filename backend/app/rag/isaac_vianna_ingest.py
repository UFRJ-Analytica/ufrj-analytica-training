"""
Pipeline de ingestao da base de conhecimento do agente de Python (Isaac Vianna).

Documento -> Loader -> Text Splitting -> Chunks -> Embedding -> ChromaDB

Executar com (o Chroma precisa estar rodando, ver docker-compose):
    .venv\\Scripts\\python -m backend.app.rag.isaac_vianna_ingest
"""
from __future__ import annotations

import time
from pathlib import Path

import chromadb
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .isaac_vianna_retriever import CHROMA_HOST, CHROMA_PORT, COLLECTION_NAME, get_vectorstore

# Pasta com os documentos da base de conhecimento (PEPs, tutorial oficial e
# material da capacitacao), ja criada pelo trainee.
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "isaac_vianna_python"

EXTENSOES_VALIDAS = {".rst", ".txt", ".md"}

# Tamanho de ~1000 caracteres cabe bem na janela de contexto do modelo e
# preserva paragrafos e exemplos de codigo inteiros; o overlap de 150
# caracteres evita cortar uma explicacao bem no meio, entre dois chunks.
TAMANHO_CHUNK = 1000
SOBREPOSICAO_CHUNK = 150

TAMANHO_LOTE = 50
MAX_TENTATIVAS = 3
ESPERA_RATE_LIMIT_SEGUNDOS = 60


def _classificar_tipo(nome_arquivo: str) -> str:
    """Classifica o documento pelo nome do arquivo, conforme a base montada."""
    if nome_arquivo.startswith("pep-"):
        return "pep"
    if nome_arquivo == "material_capacitacao.md":
        return "capacitacao"
    return "tutorial"


def _carregar_chunks() -> tuple[int, list[Document]]:
    """Le cada arquivo da base, divide em chunks e preenche a metadata."""
    arquivos_lidos = 0
    todos_chunks: list[Document] = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=TAMANHO_CHUNK, chunk_overlap=SOBREPOSICAO_CHUNK
    )

    for caminho in sorted(DATA_DIR.iterdir()):
        if caminho.suffix not in EXTENSOES_VALIDAS:
            continue

        documento = TextLoader(str(caminho), encoding="utf-8").load()
        pedacos = splitter.split_documents(documento)
        tipo = _classificar_tipo(caminho.name)

        for indice, pedaco in enumerate(pedacos):
            pedaco.metadata = {
                "source": caminho.name,
                "tipo": tipo,
                "chunk_index": indice,
            }
            todos_chunks.append(pedaco)

        arquivos_lidos += 1

    return arquivos_lidos, todos_chunks


def _enviar_lote(vectorstore, lote: list[Document], ids_lote: list[str]) -> None:
    """Envia um lote ao Chroma, com retentativa em caso de limite de taxa."""
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            vectorstore.add_documents(documents=lote, ids=ids_lote)
            return
        except Exception as exc:
            mensagem = str(exc)
            e_rate_limit = "429" in mensagem or "ResourceExhausted" in mensagem or "RESOURCE_EXHAUSTED" in mensagem
            if not e_rate_limit or tentativa == MAX_TENTATIVAS:
                raise
            print(
                f"Limite de taxa do Gemini atingido (tentativa {tentativa}/{MAX_TENTATIVAS}). "
                f"Aguardando {ESPERA_RATE_LIMIT_SEGUNDOS}s antes de tentar de novo..."
            )
            time.sleep(ESPERA_RATE_LIMIT_SEGUNDOS)


def ingerir() -> None:
    """Executa o pipeline completo de ingestao na colecao do Chroma."""
    arquivos_lidos, chunks = _carregar_chunks()
    vectorstore = get_vectorstore()

    for inicio in range(0, len(chunks), TAMANHO_LOTE):
        lote = chunks[inicio : inicio + TAMANHO_LOTE]
        ids_lote = [f"{c.metadata['source']}-{c.metadata['chunk_index']}" for c in lote]
        _enviar_lote(vectorstore, lote, ids_lote)

    # IDs deterministicos (source-chunk_index) fazem o add_documents acima
    # atualizar os itens existentes em vez de duplicar quando roda de novo.
    total_na_colecao = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT).get_collection(
        COLLECTION_NAME
    ).count()

    print(f"Arquivos lidos: {arquivos_lidos}")
    print(f"Chunks gerados: {len(chunks)}")
    print(f"Total de itens na colecao '{COLLECTION_NAME}': {total_na_colecao}")


if __name__ == "__main__":
    ingerir()
