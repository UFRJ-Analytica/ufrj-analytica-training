import os
import chromadb
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PASTA_DOCUMENTOS = os.path.join(os.path.dirname(__file__), "documentos")
NOME_COLECAO = "star_wars_docs"

# document loader: lê cada arquivo .txt da pasta
def carregar_documentos():
    documentos = []
    for nome_arquivo in os.listdir(PASTA_DOCUMENTOS):
        if nome_arquivo.endswith(".txt"):
            caminho = os.path.join(PASTA_DOCUMENTOS, nome_arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read()
            documentos.append({"texto": texto, "fonte": nome_arquivo})
    return documentos


# text splitting: quebra cada documento em chunks menores
def dividir_em_chunks(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,      # tamanho aproximado de cada chunk, em caracteres
        chunk_overlap=50,    # sobreposição entre chunks vizinhos
    )
    chunks = []
    for doc in documentos:
        pedacos = splitter.split_text(doc["texto"])
        for i, pedaco in enumerate(pedacos):
            chunks.append({
                "texto": pedaco,
                "fonte": doc["fonte"],
                "id": f"{doc['fonte']}_{i}",
            })
    return chunks


def ingerir():
    print("Carregando documentos...")
    documentos = carregar_documentos()
    print(f"{len(documentos)} documentos carregados.")

    print("Dividindo em chunks...")
    chunks = dividir_em_chunks(documentos)
    print(f"{len(chunks)} chunks gerados.")

    print("Gerando embeddings e conectando ao ChromaDB...")
    embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    client = chromadb.HttpClient(host="localhost", port=8001)
    colecao = client.get_or_create_collection(name=NOME_COLECAO)

    textos = [c["texto"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadados = [{"fonte": c["fonte"]} for c in chunks]

    vetores = embedder.embed_documents(textos)

    colecao.upsert(
        ids=ids,
        embeddings=vetores,
        documents=textos,
        metadatas=metadados,
    )

    print(f"Ingestão concluída! {len(chunks)} chunks armazenados na coleção '{NOME_COLECAO}'.")


if __name__ == "__main__":
    ingerir()