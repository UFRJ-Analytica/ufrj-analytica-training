from fastapi import APIRouter

from pydantic import BaseModel, Field
from typing import Literal

from schemas import *
from agents import evandro_rhari_agent as agent


# Criando Router

router = APIRouter(prefix='/agent/evandro-rhari-agent', tags=['evandro_rhari', 'chat'])


# Definindo modelos

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Explique o entregavel 1 para mim"])
    history: list[ChatMessage] = Field(default_factory=list)


# Tratamento de dados

def convert_history(history: list[ChatMessage]):
    return [old_message.dict() for old_message in history]


# Endpoints

@router.get('/status')
def status():
    return {'status': 'ok'}


@router.post('/chat')
def chat(request : ChatRequest):
    response = agent.chat(request.message, convert_history(request.history))
    return {"response": response}