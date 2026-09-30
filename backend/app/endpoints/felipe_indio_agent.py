from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.agents.felipe_indio_agent import agent_graph

router = APIRouter(prefix="/agent/felipe-indio", tags=["Felipe Indio"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    response = agent_graph.invoke({"messages": [("user", request.message)]})
    final_content = response["messages"][-1].content
    
    if isinstance(final_content, list):
        resposta_texto = "".join(bloco["text"] for bloco in final_content if "text" in bloco)
    else:
        resposta_texto = final_content
        
    return {"response": resposta_texto}