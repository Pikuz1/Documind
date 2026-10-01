from fastapi import APIRouter

from app.api.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> HealthOut:
    return HealthOut(status="ok")
