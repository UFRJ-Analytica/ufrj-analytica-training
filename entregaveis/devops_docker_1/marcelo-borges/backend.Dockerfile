# utilizar uma imagem base adequada;
FROM python:3.13-slim

# definir o diretório de trabalho;
WORKDIR /workdir

# copiar os arquivos necessários;
COPY . .

# instalar as dependências do backend;
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# expor a porta da aplicação;
EXPOSE 8000

# executar o FastAPI com Uvicorn.
ENTRYPOINT ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]