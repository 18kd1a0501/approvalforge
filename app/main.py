from fastapi import FastAPI, Depends
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.dependencies import get_current_user
from app.models.user import User
from app.routers import auth, workflow, approval
from app.middleware.logging import RequestLoggingMiddleware

setup_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(auth.router)
app.include_router(workflow.router)
app.include_router(approval.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}