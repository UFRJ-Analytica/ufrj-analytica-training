from fastapi import APIRouter

router = APIRouter(prefix="/luiz-paulo", tags=["luiz_paulo"])

# Rota de teste
@router.get("/status")
def status():
    return {"status": "ok", "mensagem": "funcionando"}