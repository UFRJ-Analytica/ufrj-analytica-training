from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.leticia_pessoa_agent import responder


router = APIRouter(
    prefix="/agent/leticia-pessoa",
    tags=["leticia-pessoa-agent"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    try:
        resposta = responder(payload.message)
        return ChatResponse(response=resposta)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar a mensagem: {exc}",
        )