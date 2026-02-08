import time
from fastapi import Request
from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY
import logging

logger = logging.getLogger(__name__)

async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration = time.time() - start
        path = request.url.path
        status = response.status_code if response else 500

        REQUEST_LATENCY.labels(path=path).observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            path=path,
            status=str(status),
        ).inc()

        logger.info(
            f"request handled path={path} status={status} duration={duration:.4f}"
        )
