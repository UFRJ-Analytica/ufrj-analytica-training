"""
Endpoint HTTP do Agente de Python (Isaac Vianna).

So cuida de HTTP (validacao de entrada, tratamento de erro): a logica do
agente fica em app/agents/isaac_vianna_agent.py.
"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.isaac_vianna_agent import run_isaac_vianna_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent/isaac-vianna-python", tags=["Isaac Vianna - Agente de Python"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["O que e uma list comprehension?"])


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        resposta = run_isaac_vianna_agent(request.message)
    except Exception as exc:
        logger.error("Erro ao executar o Agente de Python: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Erro ao executar o Agente de Python. Verifique os logs do backend.",
        ) from exc

    return ChatResponse(response=resposta)
