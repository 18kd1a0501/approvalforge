from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.include_router(auth.router)


@app.get("/health")
async def health():
    return {"status": "ok"}