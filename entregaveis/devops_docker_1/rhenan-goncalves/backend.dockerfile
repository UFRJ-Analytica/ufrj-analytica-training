FROM python:3.12-slim

WORKDIR /flalixo

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["fastapi","run","./app/main.py"]
