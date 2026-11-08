from fastapi import APIRouter

from app.api.schemas import HealthOut
from app.dependencies import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: SettingsDep) -> HealthOut:
    return HealthOut(status="ok", demo=settings.demo_mode)
