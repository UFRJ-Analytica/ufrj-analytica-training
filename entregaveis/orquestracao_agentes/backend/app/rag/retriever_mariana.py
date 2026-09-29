import chromadb

from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


client = chromadb.HttpClient(
    host="localhost",
    port=8001
)


collection = client.get_collection(
    name="mariana_freitas_knowledge"
)


def buscar_contexto(pergunta: str) -> str:

    query_embedding = embeddings.embed_query(pergunta)

    resultado = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documentos = resultado["documents"][0]

    if not documentos:
        return "Nenhuma informação relevante foi encontrada na base de conhecimento."

    return "\n\n---\n\n".join(documentos)