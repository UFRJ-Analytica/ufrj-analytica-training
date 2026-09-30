FROM python:3.12-slim

# Sem .pyc e com logs imediatos no `docker logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Dependências antes do código, para aproveitar o cache de build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app.py, pages/, data/, media/ (o .dockerignore filtra o resto)
COPY . .

EXPOSE 8501

# headless evita o prompt interativo; 0.0.0.0 libera acesso externo ao container
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
