from fastapi import FastAPI

from app.endpoints.kayky_leandro_endpoint import router
from app.endpoints.mariana_freitas_endpoint import router as mariana_router

app = FastAPI(
    title="MyNutri API"
)

app.include_router(router)
app.include_router(mariana_router)

@app.get("/")
def root():
    return {
        "status": "ok"
    }