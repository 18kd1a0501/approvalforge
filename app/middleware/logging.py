import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import get_logger

logger = get_logger("approvalforge.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        logger.info(
            f"rid={request_id} method={request.method} path={request.url.path} start"
        )

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            f"rid={request_id} method={request.method} path={request.url.path} "
            f"status={response.status_code} duration={duration}ms"
        )

        response.headers["X-Request-ID"] = request_id
        return response