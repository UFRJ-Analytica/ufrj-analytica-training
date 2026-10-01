from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.julio_machado_agent import responder_agente


router = APIRouter(prefix="/agent/julio_machado_agent", tags=["julio_machado"])


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str


def _dump_chat_message(message: ChatMessage) -> dict[str, str]:
    if hasattr(message, "model_dump"):
        return message.model_dump()
    return message.dict()


@router.get("/status")
def status():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Envia uma mensagem ao agente de analise de dados.

    O agente extrai numeros da mensagem, calcula estatisticas descritivas
    (media, mediana, minimo, maximo, amplitude e desvio padrao) e usa o LLM
    para interpretar e explicar os resultados.
    """
    try:
        resposta = responder_agente(
            message=request.message,
            history=[_dump_chat_message(item) for item in request.history],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar o agente de dados: {exc}",
        ) from exc

    return ChatResponse(response=resposta)
