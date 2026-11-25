import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from prometheus_client import make_asgi_app

from app.api.score import router as score_router
from app.core.logging import setup_logging
from app.core.metrics import MODEL_LOADED
from app.health import router as health_router
from app.middleware import metrics_middleware
from app.models.loader import model

setup_logging()
logger = logging.getLogger(__name__)

INDEX_HTML = Path(__file__).parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model at startup. On failure, stay up but report not ready."""
    try:
        model.load()
        logger.info(f"model loaded version={model.model_version}")
    except Exception:
        logger.error(f"model load failed, service not ready: {model.load_error}")
    MODEL_LOADED.set(1 if model.loaded else 0)
    yield


app = FastAPI(title="Content Risk Scoring", lifespan=lifespan)

app.middleware("http")(metrics_middleware)

app.include_router(score_router)
app.include_router(health_router)


@app.get("/", include_in_schema=False)
def index():
    """The one-page frontend: plain HTML, CSS and JS, no build step."""
    return FileResponse(INDEX_HTML)


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
