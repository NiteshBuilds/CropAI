from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Return the operational status of the API."""
    return HealthResponse(status="running", project="Crop AI")
