from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from app.satellite.schemas import SentinelScene, SceneCollection
from app.satellite.service import satellite_service, SatelliteServiceError

router = APIRouter(prefix="/satellite", tags=["Satellite Acquisition"])


@router.get(
    "/latest",
    response_model=Optional[SentinelScene],
    summary="Get latest Sentinel scene",
    description="Returns the most recent available Sentinel scene (Sentinel-1 or Sentinel-2) for the configured district AOI."
)
async def get_latest_scene() -> Optional[SentinelScene]:
    """Retrieve the latest scene metadata."""
    try:
        return await satellite_service.get_latest_scene()
    except SatelliteServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.get(
    "/sentinel2",
    response_model=SceneCollection,
    summary="Get Sentinel-2 scenes",
    description="Returns optical Sentinel-2 scene metadata intersecting the active district."
)
async def get_sentinel2_scenes() -> SceneCollection:
    """Retrieve Sentinel-2 scene metadata."""
    try:
        return await satellite_service.search_sentinel2()
    except SatelliteServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.get(
    "/sentinel1",
    response_model=SceneCollection,
    summary="Get Sentinel-1 scenes",
    description="Returns SAR Sentinel-1 scene metadata intersecting the active district."
)
async def get_sentinel1_scenes() -> SceneCollection:
    """Retrieve Sentinel-1 scene metadata."""
    try:
        return await satellite_service.search_sentinel1()
    except SatelliteServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@router.get(
    "/dates",
    response_model=List[str],
    summary="Get available acquisition dates",
    description="Returns a sorted list of unique acquisition dates for all available scenes."
)
async def get_available_dates() -> List[str]:
    """Retrieve all unique acquisition dates."""
    try:
        return await satellite_service.list_available_dates()
    except SatelliteServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
