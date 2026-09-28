FROM python:3.14-slim


WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY pages ./pages/
COPY data ./data/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501", "--browser.serverAddress", "0.0.0.0"]