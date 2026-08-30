# utilizar uma imagem base adequada;

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim


# definir o diretório de trabalho;
WORKDIR /workdir

# copiar os arquivos necessários;
COPY . .

# instalar as dependências do backend;
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PATH       "${PATH}:/workdir/app"
ENV PYTHONPATH "${PYTHONPATH}:/workdir/app"

# expor a porta da aplicação;
EXPOSE 8000

# executar o FastAPI com Uvicorn.
ENTRYPOINT ["python3", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]