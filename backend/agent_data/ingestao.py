import os
import chromadb
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE_DIR = os.path.dirname(__file__)
caminho_doc = os.path.abspath(os.path.join(BASE_DIR, "../agent_data/filmes.txt"))

def executar_ingestao():
    print(f"1. A carregar o documento em: {caminho_doc}")
    loader = TextLoader(caminho_doc, encoding="utf-8")
    documentos = loader.load()

    print("2. A dividir o texto em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = text_splitter.split_documents(documentos)
    print(f"Foram gerados {len(chunks)} chunks.")

    print("3. A gerar embeddings locais (HuggingFace) e a ligar ao ChromaDB via Docker...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    chroma_client = chromadb.HttpClient(host="localhost", port=8001)
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=chroma_client,
        collection_name="base_filmes"
    )
    
    print("Ingestão concluída com sucesso!")

if __name__ == "__main__":
    executar_ingestao()