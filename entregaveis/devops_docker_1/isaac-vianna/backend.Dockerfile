FROM python:3.12-slim

# Sem .pyc e com logs imediatos no `docker logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Espelha o repo: /code/backend/app/database.py sobe 3 níveis -> /code/database.db
WORKDIR /code/backend

# Dependências antes do código, para aproveitar o cache de build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 aceita conexões externas ao container; sem --reload (uso de dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
