from fastapi import APIRouter
from app.schemas.score import ScoreRequest, ScoreResponse
from app.models.loader import ModelLoader

router = APIRouter()
model = ModelLoader()
model.load()

@router.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    score = model.predict(req.content)
    label = "LOW" if score < 0.3 else "HIGH"

    return ScoreResponse(
        risk_score=score,
        risk_label=label,
        model_version=model.model_version,
    )
