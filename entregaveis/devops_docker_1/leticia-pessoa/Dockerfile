FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pages ./pages
RUN sed -i 's#http://127.0.0.1:8000#http://backend:8000#g' /app/pages/leticia_pessoa.py
COPY data ./data
COPY backend/dados ./backend/dados

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
