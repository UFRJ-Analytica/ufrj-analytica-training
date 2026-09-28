from fastapi import FastAPI

from app.endpoints.kayky_leandro_endpoint import router


app = FastAPI(
    title="MyNutri API"
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "ok"
    }