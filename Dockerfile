FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
<<<<<<< HEAD
COPY app.py .
COPY pages ./pages/
COPY data ./data/
=======
>>>>>>> develop

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pages ./pages
COPY data ./data
COPY backend/dados ./backend/dados

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]