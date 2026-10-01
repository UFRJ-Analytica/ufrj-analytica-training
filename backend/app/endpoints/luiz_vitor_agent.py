from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.luiz_vitor_agent import responder_agente

router = APIRouter(prefix="/agent/luiz-vitor", tags=["luiz_vitor"])

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        response = responder_agente(message=request.message, history=history_dicts)
        return ChatResponse(response=response)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro interno: {exc}") from exc