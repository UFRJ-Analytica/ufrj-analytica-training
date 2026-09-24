# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos necessários para o contêiner
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código para o contêiner
COPY . .

# Defina o comando padrão para executar o aplicativo
CMD ["python", "main.py"]