# utilizar uma imagem base adequada;
FROM python:3.13-slim

# definir o diretório de trabalho;
WORKDIR /workdir

# copiar os arquivos necessários;
COPY requirements.txt .
COPY app.py .
COPY pages ./pages/
COPY data ./data/

# instalar as dependências do frontend;
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# expor a porta utilizada pela aplicação;
EXPOSE 8501

# iniciar corretamente o frontend
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501"]