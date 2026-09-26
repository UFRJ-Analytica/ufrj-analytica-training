FROM python:3.12-slim

WORKDIR /backend
#Copiar só o requirements, para instalar os requirements
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
#Copiar o diretório base para rodar app.py
COPY backend .
#A princípio vou rodar só o meu, para funcionar
RUN rm -rf /backend/app/endpoints/*
COPY backend/app/endpoints/giovanni_almeida.py /backend/app/endpoints/

ENV PYTHONPATH=/backend
ENV PYTHONPATH=${PYTHONPATH}:/backend/app    

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]