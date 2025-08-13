from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
def health():
    return {"ok": True}

@router.get("/readyz")
def ready():
    return {"ready": True}
