from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.agents.julio_menescal_agent import responder_agente

router = APIRouter(
    prefix="/agent/julio-menescal",
    tags=["julio_menescal_agent"],
)

class HistoryMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = []

class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        historico = [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in request.history
        ]

        resposta = responder_agente(
            request.message,
            historico,
        )

        return ChatResponse(response=resposta)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar o agente: {exc}",
        ) from exc