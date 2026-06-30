from fastapi import APIRouter, HTTPException

from app.schemas.moisture_stress import MoistureStressRequest, MoistureStressResponse
from app.services.moisture_stress_service import moisture_stress_service

router = APIRouter(prefix="/moisture-stress", tags=["Moisture Stress"])


@router.get(
    "/sample",
    response_model=MoistureStressResponse,
    summary="Get sample moisture stress assessment",
    description="Returns a realistic sample moisture stress response for the Sehore district context.",
)
async def get_moisture_stress_sample() -> MoistureStressResponse:
    """Return a realistic sample moisture stress assessment."""
    return moisture_stress_service.build_sample_response()


@router.post(
    "/analyze",
    response_model=MoistureStressResponse,
    summary="Analyze crop moisture stress",
    description=(
        "Fuses Sentinel-2 vegetation indices with Open-Meteo weather data "
        "to estimate crop moisture stress using a rule-based engine."
    ),
)
async def analyze_moisture_stress(
    request: MoistureStressRequest,
) -> MoistureStressResponse:
    """Run the moisture stress detection engine for the given field observation."""
    try:
        return await moisture_stress_service.analyze_stress(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
