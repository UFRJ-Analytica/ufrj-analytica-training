# utilizar uma imagem base adequada;

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim


# definir o diretório de trabalho;
WORKDIR /workdir

# copiar os arquivos necessários;
# (poderia ter sido usado um .dockerignore, mas achei essa forma mais simples e estável
COPY requirements.txt .
COPY app.py .
COPY pages ./pages/
COPY data ./data/


# instalar as dependências do frontend;
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV PATH       "${PATH}:/workdir/app"
ENV PYTHONPATH "${PYTHONPATH}:/workdir/app"


# expor a porta utilizada pela aplicação;
EXPOSE 8501

# iniciar corretamente o frontend
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501", "--browser.serverAddress", "0.0.0.0"]