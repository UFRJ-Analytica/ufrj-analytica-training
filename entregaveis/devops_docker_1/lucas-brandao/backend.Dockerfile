FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code/backend

COPY requirements.txt .

RUN grep -v "chromadb" requirements.txt > req_clean.txt

RUN pip install --no-cache-dir -r req_clean.txt

RUN pip install --no-cache-dir chromadb==1.5.9 langchain-community langchain-text-splitters langchain-huggingface

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]