import chromadb


client = chromadb.HttpClient(
    host="localhost",
    port=8001
)


print("Conectando ao ChromaDB...")

heartbeat = client.heartbeat()

print(f"ChromaDB respondeu: {heartbeat}")