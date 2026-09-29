# utilizar uma imagem base adequada;
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

# definir o diretório de trabalho;
WORKDIR /workdir

# instalar as dependências do frontend;
# (requirements copiado antes do código para aproveitar o cache de camadas)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copiar os arquivos necessários;
COPY app.py .
COPY pages ./pages/
COPY data ./data/
COPY media ./media/

# expor a porta utilizada pela aplicação;
EXPOSE 8501

# iniciar corretamente o frontend
# (--server.address 0.0.0.0 faz o Streamlit aceitar conexões de fora do container)
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]