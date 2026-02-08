from fastapi import FastAPI
from app.api.score import router as score_router
from app.health import router as health_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="Content Risk Scoring")

app.include_router(score_router)
app.include_router(health_router)
