from pydantic import BaseModel, ConfigDict, Field


class ScoreRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class ScoreResponse(BaseModel):
    # Pydantic reserves the "model_" prefix; allow the model_version field without a warning.
    model_config = ConfigDict(protected_namespaces=())

    risk_score: float
    risk_label: str
    model_version: str
    degraded: bool = False
