# utilizar uma imagem base adequada;
ARG PYTHON_VERSION=3.14.4
FROM python:${PYTHON_VERSION}-slim

# definir o diretório de trabalho;
WORKDIR /workdir

# instalar as dependências do frontend;
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copiar os arquivos necessários;
COPY requirements.txt .
COPY app.py .
COPY pages ./pages/
COPY data ./data/

# expor a porta utilizada pela aplicação;
EXPOSE 8501

# iniciar corretamente o frontend
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]