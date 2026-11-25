import logging
import time

from fastapi import Request

from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY

logger = logging.getLogger(__name__)

UNMATCHED = "unmatched"


def _is_metrics_path(path: str) -> bool:
    return path == "/metrics" or path.startswith("/metrics/")


def _route_template(request: Request) -> str:
    """The matched route's template (e.g. /score), set by the router after matching."""
    route = request.scope.get("route")
    return getattr(route, "path", UNMATCHED)


async def metrics_middleware(request: Request, call_next):
    if _is_metrics_path(request.url.path):
        return await call_next(request)

    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration = time.perf_counter() - start
        path = _route_template(request)
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
