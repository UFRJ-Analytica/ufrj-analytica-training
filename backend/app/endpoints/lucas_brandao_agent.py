from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal

from app.agents import lucas_brandao_agent as agent

router = APIRouter(
    prefix='/agent/lucas-brandao-agent',
    tags=['lucas_brandao', 'chat', 'viagens']
)

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Sugira uma rota começando por Marrocos."])
    history: list[ChatMessage] = Field(default_factory=list)

def convert_history(history: list[ChatMessage]):
    return [old_message.dict() for old_message in history]

@router.get('/status')
def status():
    return {'status': 'ok'}

@router.post('/chat')
def chat(request: ChatRequest):
    response = agent.chat_com_agente(
        mensagem_usuario=request.message, 
        history=convert_history(request.history)
    )
    return {"response": response}