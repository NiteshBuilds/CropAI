"""
advisory.py  (api router)
──────────────────────────
Router prefix : /api/advisory
Tag           : Advisory

Endpoints
---------
GET  /api/advisory/sample    — demo response, no inputs required
POST /api/advisory/generate  — full advisory from field parameters
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from app.services.advisory_service import advisory_service

router = APIRouter(prefix="/advisory", tags=["Advisory"])


@router.get(
    "/sample",
    response_model=AdvisoryResponse,
    summary="Get sample farmer advisory",
    description=(
        "Returns a realistic hardcoded advisory message for demonstration "
        "and Swagger documentation purposes. No inputs required."
    ),
)
async def get_advisory_sample() -> AdvisoryResponse:
    """Return a pre-built sample farmer advisory."""
    return advisory_service.build_sample_response()


@router.post(
    "/generate",
    response_model=AdvisoryResponse,
    summary="Generate farmer advisory",
    description=(
        "Accepts field parameters, internally calls Moisture Stress, Irrigation "
        "and Weather services, and returns a plain-language farmer advisory."
    ),
)
async def generate_advisory(request: AdvisoryRequest) -> AdvisoryResponse:
    """Run the full advisory pipeline for the given field observation."""
    try:
        return await advisory_service.generate(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advisory engine failed: {exc}",
        ) from exc
