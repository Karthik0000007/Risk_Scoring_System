from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
def health():
    return {"status": "ok"}

@router.get("/readyz")
def ready():
    return {"ready": True}
