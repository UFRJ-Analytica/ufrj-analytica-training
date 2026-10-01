from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.agents.joao_rodrigo_agent import responder_agente

router = APIRouter(prefix="/agent/joao-rodrigo", tags=["joao_rodrigo"])

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, examples=["Recomende um rock pra ouvir descalço"])

class ChatResponse(BaseModel):
    response: str

# endpoints ---

@router.get('/status')
def status():
    return {'status': 'ok'}

@router.post("/chat", response_model=ChatResponse)
def chat_joao(request: ChatRequest):
    resposta_agente_raw = responder_agente(request.message)
    
    # tratando resposta
    if isinstance(resposta_agente_raw, list) and len(resposta_agente_raw) > 0:
        resposta = resposta_agente_raw[0].get("text", str(resposta_agente_raw))
    else:
        resposta = str(resposta_agente_raw)
        
    return ChatResponse(response=resposta)