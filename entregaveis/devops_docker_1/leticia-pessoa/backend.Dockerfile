FROM python:3.14-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt

# Remove apenas dentro da imagem a versão conflitante antiga do ChromaDB
RUN grep -v '^chromadb>=0\.6\.3,<1\.0\.0$' requirements.txt > /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Copia o backend atual
COPY backend/app ./app
COPY backend/dados ./dados

# Adiciona os schemas compatíveis com a API da Leticia
COPY entregaveis/devops_docker_1/leticia-pessoa/leticia_schemas.py ./app/leticia_schemas.py

# Faz somente a cópia containerizada do endpoint da Leticia usar esses schemas
RUN sed -i 's/from app\.schemas import/from app.leticia_schemas import/' \
    /app/app/endpoints/leticia_pessoa.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
