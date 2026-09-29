"""
API standalone do Agente de Filmes.

Este módulo sobe seu PRÓPRIO app FastAPI, em vez de um router a ser
incluído no main.py compartilhado do projeto — assim não é preciso alterar
nenhum arquivo usado por outros trainees.

Rodar (a partir da raiz do repositório):
    uvicorn backend.app.endpoints.gabriel_basto_agent:app --reload --port 8010

Depois, o Swagger fica em:
    http://127.0.0.1:8010/docs
"""
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.agents.gabriel_basto_agent import run_agent

# Carrega backend/.env explicitamente (independe de onde o comando é rodado)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="Agente de Filmes — Gabriel Basto", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {"status": "ok", "agente": "filmes"}


@app.post("/agent/filmes/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="A mensagem não pode estar vazia.")
    try:
        resposta = run_agent(request.message)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Erro ao processar a mensagem: {exc}") from exc
    return ChatResponse(response=resposta)
