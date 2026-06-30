"""
config.py (api router)
──────────────────────
Endpoints for retrieving the District Intelligence Module configuration.
"""

from typing import Dict
from fastapi import APIRouter

from app.schemas.config import DistrictConfig, SeasonConfig, CropCalendarEntry
from app.services.config_service import config_service

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.get(
    "",
    response_model=DistrictConfig,
    summary="Get complete district configuration",
    description="Returns the full configuration for the active district intelligence module.",
)
async def get_full_configuration() -> DistrictConfig:
    """Return the complete district configuration."""
    return config_service.get_full_configuration()


@router.get(
    "/crops",
    response_model=Dict[str, CropCalendarEntry],
    summary="Get supported crops and calendar",
    description="Returns the crop calendar containing only the supported crops for the active district.",
)
async def get_crops() -> Dict[str, CropCalendarEntry]:
    """Return the crop calendar."""
    return config_service.get_crop_calendar()


@router.get(
    "/season",
    response_model=SeasonConfig,
    summary="Get season information",
    description="Returns the configured growing season information for the active district.",
)
async def get_season() -> SeasonConfig:
    """Return season information."""
    return config_service.get_season()
