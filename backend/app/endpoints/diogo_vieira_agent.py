from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.diogo_vieira_agent import responder_agente, status_agente

router = APIRouter(prefix="/agent/diogo-vieira", tags=["diogo_vieira", "chat"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Me recomende um RPG para Nintendo Switch"])
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str


@router.get("/health")
def health():
    return status_agente()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = responder_agente(
            message=request.message,
            history=[item.model_dump() for item in request.history],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        # ex.: chave de API não configurada
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar o agente: {exc}",
        ) from exc

    return ChatResponse(response=response)