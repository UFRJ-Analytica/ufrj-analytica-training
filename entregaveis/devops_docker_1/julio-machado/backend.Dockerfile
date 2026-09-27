FROM python:3.12-slim


WORKDIR /app

COPY backend/. /app/backend/

WORKDIR /app/backend

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

ENTRYPOINT ["python3", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]