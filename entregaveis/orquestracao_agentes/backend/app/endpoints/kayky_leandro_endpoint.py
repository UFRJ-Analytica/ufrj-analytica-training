from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent.kayky_leandro_agent import executar_agente

router = APIRouter(
    prefix="/agent/mynutri",
    tags=["MyNutri"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        resposta = executar_agente(request.message)

        return {
            "response": resposta
        }

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=str(erro)
        )