from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.sgcont_agent import responder_agente, status_agente


router = APIRouter(prefix="/agent/sgcont", tags=["sgcont_agent"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Como faco o entregavel 1?"])
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str


def _dump_chat_message(message: ChatMessage) -> dict[str, str]:
    if hasattr(message, "model_dump"):
        return message.model_dump()
    return message.dict()


@router.get("/health")
def health():
    return status_agente()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = responder_agente(
            message=request.message,
            history=[_dump_chat_message(item) for item in request.history],
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Mensagem invalida.")
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao executar o agente.")

    return ChatResponse(response=response)
