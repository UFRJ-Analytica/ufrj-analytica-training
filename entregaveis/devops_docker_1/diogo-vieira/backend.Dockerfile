# utilizar uma imagem base adequada;
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

# definir o diretório de trabalho;
WORKDIR /workdir

# instalar as dependências do backend;
# (contexto de build = raiz do projeto, onde está o requirements.txt)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copiar os arquivos da API;
COPY backend/ .

# expor a porta da aplicação;
EXPOSE 8000

# executar o FastAPI com Uvicorn.
ENTRYPOINT ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]