# utilizar uma imagem base adequada;

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY data/ ./data/
COPY pages/ ./pages/

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--browser.serverAddress", "0.0.0.0"]
