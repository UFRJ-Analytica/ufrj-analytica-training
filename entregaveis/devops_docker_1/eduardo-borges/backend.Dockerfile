# Arquivo: ufrj-analytica-training/backend/Dockerfile
FROM python:3.10-slim       

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da API
COPY . .

# Expõe a porta da aplicação
EXPOSE 8000

# Executa o FastAPI com Uvicorn, aceitando conexões externas ao container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]