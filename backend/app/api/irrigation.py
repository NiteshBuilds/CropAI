"""
irrigation.py  (api router)
────────────────────────────
Router prefix : /api/irrigation
Tag           : Irrigation

Endpoints
---------
GET  /api/irrigation/sample      — demo response, no inputs required
POST /api/irrigation/recommend   — full advisory from field parameters
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.irrigation import IrrigationRequest, IrrigationResponse
from app.services.irrigation_service import irrigation_service

router = APIRouter(prefix="/irrigation", tags=["Irrigation"])


@router.get(
    "/sample",
    response_model=IrrigationResponse,
    summary="Get sample irrigation recommendation",
    description=(
        "Returns a realistic hardcoded irrigation advisory for demonstration "
        "and API documentation purposes. No field parameters required."
    ),
)
async def get_irrigation_sample() -> IrrigationResponse:
    """Return a pre-built sample irrigation recommendation."""
    # Access the private helper through the service instance
    return irrigation_service._build_sample_response()


@router.post(
    "/recommend",
    response_model=IrrigationResponse,
    summary="Generate irrigation recommendation",
    description=(
        "Accepts field parameters, internally calls the Moisture Stress "
        "and Weather services, and returns a structured irrigation advisory."
    ),
)
async def recommend_irrigation(request: IrrigationRequest) -> IrrigationResponse:
    """Run the irrigation advisory engine for the given field observation."""
    try:
        return await irrigation_service.recommend(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Irrigation advisory engine failed: {exc}",
        ) from exc
