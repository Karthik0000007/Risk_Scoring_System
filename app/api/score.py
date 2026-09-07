from fastapi import APIRouter
from app.schemas.score import ScoreRequest, ScoreResponse
from app.models.loader import ModelLoader
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

model = ModelLoader()
model.load()


def _classify(score: float) -> str:
    """Map a numeric risk score to a human-readable label."""
    if score < 0.3:
        return "LOW"
    elif score <= 0.6:
        return "MEDIUM"
    else:
        return "HIGH"


@router.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    try:
        score_value = model.predict(req.content)
        label = _classify(score_value)

        return ScoreResponse(
            risk_score=score_value,
            risk_label=label,
            model_version=model.model_version,
        )

    except Exception as e:
        logger.error(f"inference failed: {e}")

        return ScoreResponse(
            risk_score=0.5,
            risk_label="UNKNOWN",
            model_version=model.model_version,
        )
