from pathlib import Path

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parents[3]

CHROMA_DIR = BASE_DIR / "chroma_data"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


vectorstore = Chroma(
    client=client,
    collection_name="mynutri",
    embedding_function=embeddings,
)


retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 3
    }
)


def buscar_contexto(pergunta: str) -> str:

    documentos = retriever.invoke(pergunta)

    if not documentos:
        return "Nenhuma informação relevante foi encontrada na base de conhecimento."

    contextos = []

    for documento in documentos:

        fonte = documento.metadata.get(
            "source",
            "fonte desconhecida"
        )

        pagina = documento.metadata.get(
            "page",
            "?"
        )

        contextos.append(
            f"Fonte: {fonte} | Página: {pagina}\n"
            f"{documento.page_content}"
        )

    return "\n\n---\n\n".join(contextos)