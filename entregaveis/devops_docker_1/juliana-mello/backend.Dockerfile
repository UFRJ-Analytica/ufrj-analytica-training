FROM python:3.11-slim

WORKDIR /app

# instala o curl para o healthcheck funcionar
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# problema: no meu database.py fala pra subir 3 pastas pra achar o databse.db.
# isso funciona pq databse.db ta na raiz do meu reposiotiro, mas nao funciona para o conatiner, ja que subiria 3 pastas de onde ele ta, e la nao teria o databse.db
# pra tentar consertar isso, copiei os qruivos pra dentro do conatiner de forma a respeitar a profundidade do reposiotiro real

# copia pendencias do backend e instala
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# copia o código da API para dentro da pasta backend/
COPY backend/app ./backend/app
# agora, subindo 3 a partir de database.py, chega em /app (raiz do workdir), onde eu copiei databse.db

# copia o banco de dados que fica na raiz do repositorio
COPY database.db ./database.db

# muda o diretorio de trabalho pra dentro de backend/, reproduzindo onde eu rodava o uvicorn localmente
WORKDIR /app/backend

# fastapi/uvicorn por padrao na porta 8000
EXPOSE 8000

# inicia o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# "--host 0.0.0.0" é equivalente ao "--server.address" do streamlit, sem isso o uvicorn so aceita conexoes dentro do proprio container
