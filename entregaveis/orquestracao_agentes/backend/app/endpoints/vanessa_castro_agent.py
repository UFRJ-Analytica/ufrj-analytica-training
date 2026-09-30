from fastapi import APIRouter
from pydantic import BaseModel
from app.agent.vanessa_castro_agent import run_vanessa_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/agent/vanessa-castro/chat")
async def chat_with_agent(request: ChatRequest):
    resposta = run_vanessa_agent(request.message)
    return {"response": resposta}