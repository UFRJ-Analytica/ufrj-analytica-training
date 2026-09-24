from pathlib import Path
import hashlib

import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parents[3]

DOCS_DIR = BASE_DIR / "docs" / "mynutri"
CHROMA_DIR = BASE_DIR / "chroma_data"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


documentos = []

for arquivo in DOCS_DIR.glob("*.pdf"):
    print(f"Carregando: {arquivo.name}")

    loader = PyPDFLoader(str(arquivo))

    documentos.extend(loader.load())


print(f"Documentos carregados: {len(documentos)}")


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


chunks = splitter.split_documents(documentos)


print(f"Chunks criados: {len(chunks)}")


ids = []

for i, chunk in enumerate(chunks):

    hash_texto = hashlib.md5(
        chunk.page_content.encode("utf-8")
    ).hexdigest()

    ids.append(
        f"chunk_{i}_{hash_texto}"
    )


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


vectorstore = Chroma(
    client=client,
    collection_name="mynutri",
    embedding_function=embeddings,
    collection_metadata={
        "hnsw:space": "cosine"
    },
)


existing_ids = set(
    vectorstore._collection.get()["ids"]
)


novos_chunks = []
novos_ids = []


for chunk, chunk_id in zip(chunks, ids):

    if chunk_id not in existing_ids:

        novos_chunks.append(chunk)
        novos_ids.append(chunk_id)


print(
    f"Chunks novos para inserir: {len(novos_chunks)}"
)


if novos_chunks:

    vectorstore.add_documents(
        documents=novos_chunks,
        ids=novos_ids
    )

    print(
        f"{len(novos_chunks)} chunks adicionados ao Chroma."
    )

else:

    print("Nenhum chunk novo.")


print(
    f"Total na collection: {vectorstore._collection.count()}"
)