from pydantic import BaseModel

class Settings(BaseModel):
    service_name: str = "content-risk-scoring"
    environment: str = "local"

settings = Settings()
