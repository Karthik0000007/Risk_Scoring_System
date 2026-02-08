from fastapi import APIRouter
from app.schemas.score import ScoreRequest, ScoreResponse
from app.models.loader import ModelLoader
import logging
import time
time.sleep(0.2)

logger = logging.getLogger(__name__)

router = APIRouter()

model = ModelLoader()
model.load()


@router.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    try:
        score_value = model.predict(req.content)
        label = "LOW" if score_value < 0.3 else "HIGH"

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
