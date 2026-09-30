FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
#Copiar o diretório base para rodar app.py
COPY / . 

ENV BASE_URL="http://127.0.0.1:8000//"

EXPOSE 8501

CMD ["streamlit", "run","app.py"]
