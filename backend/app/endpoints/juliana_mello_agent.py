from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from backend.app.agents.juliana_mello_agent import agent_graph, extrair_texto_resposta

router = APIRouter(prefix='/agent/juliana-mello', tags=['juliana_mello', 'chat'])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat_juliana_mello(request: ChatRequest) -> ChatResponse:
    resultado = agent_graph.invoke({
        "messages": [HumanMessage(content=request.message)]
    })
    ultima_mensagem = resultado["messages"][-1]
    return ChatResponse(response=extrair_texto_resposta(ultima_mensagem))