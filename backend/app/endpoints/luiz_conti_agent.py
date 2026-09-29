"""API de conversa com o tutor de análise de dados."""

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.luiz_conti_agent import responder_agente

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent/luiz-conti", tags=["Luiz Conti - Agente"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8_000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8_000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = responder_agente(
            request.message,
            [{"role": item.role, "content": item.content} for item in request.history],
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Falha ao processar mensagem do agente")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter uma resposta do agente.",
        ) from exc
    return ChatResponse(response=response)
