from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.pedro_ferrari_agent import executar_agente


router = APIRouter(
    prefix="/agent/pedro-ferrari",
    tags=["Pedro Ferrari - GAMEni"]
)


class MensagemHistorico(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[MensagemHistorico] = Field(
        default_factory=list
    )


class ChatResponse(BaseModel):
    response: str


@router.get("/status")
def status():
    return {
        "status": "ok",
        "agent": "GAMEni"
    }


@router.post("/chat", response_model=ChatResponse)
def chat(dados: ChatRequest):
    historico = []

    for mensagem in dados.history:
        item = {
            "role": mensagem.role,
            "content": mensagem.content
        }

        historico.append(item)

    try:
        resposta = executar_agente(
            dados.message,
            historico
        )

        return {
            "response": resposta
        }

    except Exception as erro:
        texto_erro = str(erro)

        if "RESOURCE_EXHAUSTED" in texto_erro:
            raise HTTPException(
                status_code=429,
                detail="Limite da API Gemini atingido."
            )

        if "503 UNAVAILABLE" in texto_erro:
            raise HTTPException(
                status_code=503,
                detail="Gemini temporariamente indisponível."
            )

        raise HTTPException(
            status_code=500,
            detail="Erro ao executar o agente."
        )