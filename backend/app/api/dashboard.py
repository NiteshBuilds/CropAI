"""
dashboard.py  (api router)
───────────────────────────
Router prefix : /api/dashboard
Tag           : Dashboard

Endpoints
---------
GET  /api/dashboard/sample   — hardcoded demo payload, no inputs needed
POST /api/dashboard/summary  — live aggregation from all AI engines
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.dashboard import DashboardRequest, DashboardResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/sample",
    response_model=DashboardResponse,
    summary="Get sample dashboard payload",
    description=(
        "Returns a realistic hardcoded dashboard payload combining satellite indices, "
        "moisture stress, irrigation recommendation and farmer advisory. "
        "Ideal for frontend development and demo presentations."
    ),
)
async def get_dashboard_sample() -> DashboardResponse:
    """Return a pre-built sample dashboard payload."""
    return dashboard_service.build_sample_response()


@router.post(
    "/summary",
    response_model=DashboardResponse,
    summary="Generate live dashboard summary",
    description=(
        "Accepts field parameters and aggregates outputs from all AI engines "
        "(Sentinel-2 Processing → Moisture Stress → Irrigation → Advisory) "
        "into a single dashboard-ready response."
    ),
)
async def get_dashboard_summary(request: DashboardRequest) -> DashboardResponse:
    """Run the full aggregation pipeline and return a dashboard summary."""
    try:
        return await dashboard_service.get_summary(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard aggregation failed: {exc}",
        ) from exc
