ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY data/ ./data/
COPY pages/ ./pages/

RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# executando o streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]