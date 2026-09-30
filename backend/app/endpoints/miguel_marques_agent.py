import logging

from fastapi import APIRouter, HTTPException
from openai import RateLimitError
from pydantic import BaseModel, Field

# Importa a função de entrada do agente 
from ..agents.miguel_marques_agent import executar_agente

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent/miguel-marques-agent", tags=["Agente Docker Miguel Marques"])



class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="Mensagem do usuário")


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        return ChatResponse(response=executar_agente(req.message))
    except RuntimeError as erro:          
        raise HTTPException(status_code=503, detail=str(erro))
    except RateLimitError:                
        raise HTTPException(
            status_code=429,
            detail="O modelo está ocupado no momento. Tente novamente em instantes.",
        )
    except Exception:                     # qualquer outra falha inesperada
        logger.exception("Falha ao executar o agente")
        raise HTTPException(status_code=502, detail="Falha ao processar a mensagem no agente.")