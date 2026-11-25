import logging

from fastapi import APIRouter, HTTPException

from app.core.metrics import FALLBACKS, PREDICTIONS
from app.models.loader import fallback, model
from app.schemas.score import ScoreRequest, ScoreResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _classify(score: float) -> str:
    """Map a numeric risk score to a human-readable label."""
    if score < 0.3:
        return "LOW"
    elif score <= 0.6:
        return "MEDIUM"
    else:
        return "HIGH"


def _response(score_value: float, version: str, degraded: bool) -> ScoreResponse:
    return ScoreResponse(
        risk_score=score_value,
        risk_label=_classify(score_value),
        model_version=version,
        degraded=degraded,
    )


@router.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    if not model.loaded:
        raise HTTPException(status_code=503, detail="model not loaded")
    response = _predict(req.content)
    PREDICTIONS.labels(label=response.risk_label).inc()
    return response


def _predict(text: str) -> ScoreResponse:
    """Model first; keyword fallback if it raises; UNKNOWN if both fail."""
    try:
        return _response(model.predict(text), model.model_version, False)
    except Exception as e:
        logger.error(f"model inference failed, using keyword fallback: {e}")

    FALLBACKS.inc()
    try:
        return _response(fallback.predict(text), fallback.version, True)
    except Exception as e:
        logger.error(f"keyword fallback failed: {e}")
        return ScoreResponse(
            risk_score=0.5,
            risk_label="UNKNOWN",
            model_version=fallback.version,
            degraded=True,
        )
