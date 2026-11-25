from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.loader import model

router = APIRouter()


@router.get("/healthz")
def health():
    """Liveness: the process is up, whether or not the model loaded."""
    return {"status": "ok"}


@router.get("/readyz")
def ready():
    """Readiness: only ready to take traffic once the model is loaded."""
    if model.loaded:
        return {"ready": True, "model_version": model.model_version}
    reason = model.load_error or "model not loaded"
    return JSONResponse(status_code=503, content={"ready": False, "reason": reason})
