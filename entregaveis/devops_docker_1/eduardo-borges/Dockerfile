FROM python:3.10-slim

WORKDIR /app

# Copia e instala as dependências da raiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação (app.py, pages, data, etc.)
COPY . .

# Expõe a porta (8501 é o padrão do Streamlit; ajuste se for outra)
EXPOSE 8501

# Comando para rodar a aplicação principal
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]