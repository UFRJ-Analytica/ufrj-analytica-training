from fastapi import FastAPI

from app.endpoints.kayky_leandro_endpoint import router
from app.endpoints.vanessa_castro_agent import router as vanessa_router

app = FastAPI(
    title="MyNutri API"
)

app.include_router(router)
app.include_router(vanessa_router, tags=["Vanessa Castro"])

@app.get("/")
def root():
    return {
        "status": "ok"
    }