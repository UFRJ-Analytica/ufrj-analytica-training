from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.rhenan_goncalves_agent import responder_agente, status_agente


router = APIRouter(prefix="/agent/rhenan-agent", tags=["agente_rhenan"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Oi Carlinhos bom dia"])
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
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar o agente: {exc}",
        ) from exc

    return ChatResponse(response=response)
