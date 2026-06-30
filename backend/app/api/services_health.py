"""
services_health.py  (api router)
─────────────────────────────────
Endpoint: GET /api/health/services

Returns the configuration status of each external service by probing the
local environment only — no network calls are made.
"""

from fastapi import APIRouter

from app.core.api_config import copernicus_config, sentinel_hub_config, open_meteo_config
from app.schemas.services_health import ServicesHealthResponse, ServiceStatus

router = APIRouter(prefix="/health", tags=["Health"])


def _service_status(is_configured: bool) -> ServiceStatus:
    return "configured" if is_configured else "not_configured"


@router.get(
    "/services",
    response_model=ServicesHealthResponse,
    summary="External service configuration status",
    description=(
        "Checks whether each external service (Copernicus, Sentinel Hub, Open-Meteo) "
        "is configured via environment variables. No network requests are made."
    ),
)
async def services_health() -> ServicesHealthResponse:
    """Return configuration status for all external data services."""
    return ServicesHealthResponse(
        copernicus=_service_status(copernicus_config.is_configured),
        sentinel=_service_status(sentinel_hub_config.is_configured),
        weather=_service_status(open_meteo_config.is_configured),
    )
