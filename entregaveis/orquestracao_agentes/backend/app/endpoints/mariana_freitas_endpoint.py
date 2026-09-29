from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.mariana_freitas_agent import chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/agent/mariana-freitas/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    response = chat(request.message)
    return {"response": response}