ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

# diretório de trabalho
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos necessários do frontend
COPY app.py .
COPY pages ./pages
COPY data ./data
COPY backend/dados ./backend/dados

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]