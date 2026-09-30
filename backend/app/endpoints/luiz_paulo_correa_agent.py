from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.luiz_paulo_correa_agent import responder_agente, status_agente

router = APIRouter(prefix="/agent/luiz-paulo", tags=["luiz_paulo_agente"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Que artigos voces tem sobre clustering?"])
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str


@router.get("/status")
def status():
    return status_agente()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        resposta = responder_agente(
            message=request.message,
            history=[item.model_dump() for item in request.history],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao executar o agente: {exc}") from exc

    return ChatResponse(response=resposta)
