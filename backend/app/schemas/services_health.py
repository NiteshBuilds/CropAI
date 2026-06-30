"""
services_health.py
──────────────────
Pydantic response schema for the /api/health/services endpoint.
"""

from typing import Literal
from pydantic import BaseModel

ServiceStatus = Literal["configured", "not_configured"]


class ServicesHealthResponse(BaseModel):
    """Per-service configuration status returned by /api/health/services."""

    copernicus: ServiceStatus
    sentinel: ServiceStatus
    weather: ServiceStatus
