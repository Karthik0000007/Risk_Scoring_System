from fastapi import FastAPI
from prometheus_client import make_asgi_app
from app.middleware import metrics_middleware
from app.api.score import router as score_router
from app.health import router as health_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="Content Risk Scoring")

app.middleware("http")(metrics_middleware)

app.include_router(score_router)
app.include_router(health_router)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
