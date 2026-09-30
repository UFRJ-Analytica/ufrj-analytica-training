# utilizar uma imagem base adequada;
ARG PYTHON_VERSION=3.14.4
FROM python:${PYTHON_VERSION}-slim

# definir o diretório de trabalho;
WORKDIR /workdir

# instalar as dependências do backend;
COPY requirements.txt .

RUN sed -i '/^chromadb[<>]/d' requirements.txt \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copiar os arquivos necessários;
COPY . .


RUN ln -sf /data/database.db '/workdir/entregaveis\banco_de_dados\luiz_conti_trainee\database.db'

# expor a porta da aplicação;
EXPOSE 8000

# executar o FastAPI com Uvicorn (aceitando conexões externas ao container).
ENTRYPOINT ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
