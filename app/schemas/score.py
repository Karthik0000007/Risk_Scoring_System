from pydantic import BaseModel, Field

class ScoreRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class ScoreResponse(BaseModel):
    risk_score: float
    risk_label: str
    model_version: str
