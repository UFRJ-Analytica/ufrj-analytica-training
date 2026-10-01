from pathlib import Path
import hashlib

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parents[3]

DOCS_DIR = BASE_DIR / "knowledge" / "documents"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


documentos = []

for arquivo in DOCS_DIR.glob("*.txt"):
    print(f"Carregando: {arquivo.name}")

    texto = arquivo.read_text(encoding="utf-8")

    documentos.append({
        "texto": texto,
        "source": arquivo.name
    })


print(f"Documentos carregados: {len(documentos)}")


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


chunks = []

for documento in documentos:

    textos = splitter.split_text(documento["texto"])

    for texto in textos:
        chunks.append({
            "texto": texto,
            "source": documento["source"]
        })


print(f"Chunks criados: {len(chunks)}")


client = chromadb.HttpClient(
    host="localhost",
    port=8001
)


collection = client.get_or_create_collection(
    name="mariana_freitas_knowledge",
    metadata={
        "hnsw:space": "cosine"
    }
)


existing_ids = set(collection.get()["ids"])


novos_chunks = []
novos_ids = []


for i, chunk in enumerate(chunks):

    hash_texto = hashlib.md5(
        chunk["texto"].encode("utf-8")
    ).hexdigest()

    chunk_id = f"mariana_chunk_{i}_{hash_texto}"

    if chunk_id not in existing_ids:
        novos_chunks.append(chunk)
        novos_ids.append(chunk_id)


print(f"Chunks novos para inserir: {len(novos_chunks)}")


if novos_chunks:

    textos = [
        chunk["texto"]
        for chunk in novos_chunks
    ]

    vetores = embeddings.embed_documents(textos)

    collection.add(
        ids=novos_ids,
        documents=textos,
        embeddings=vetores,
        metadatas=[
            {"source": chunk["source"]}
            for chunk in novos_chunks
        ]
    )

    print(
        f"{len(novos_chunks)} chunks adicionados ao Chroma."
    )

else:

    print("Nenhum chunk novo.")


print(
    f"Total na collection: {collection.count()}"
)