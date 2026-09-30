from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.sylvio_helt_agent import MODEL_CONFIG, TOOLS, responder_agente


router = APIRouter(prefix="/agent/agente-financeiro", tags=["sylvio_helt_agent"])


class Mensagem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Quanto rendem 500 reais a 0,8% ao mês por 2 anos?"])
    history: list[Mensagem] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str


@router.get("/health")
def health():
    return {
        "agent": "agente_financeiro",
        "model": MODEL_CONFIG["model"],
        "tools": [t.name for t in TOOLS],
    }


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        resposta = responder_agente(
            message=request.message,
            history=[m.model_dump() for m in request.history],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao executar o agente: {exc}") from exc

    return ChatResponse(response=resposta)