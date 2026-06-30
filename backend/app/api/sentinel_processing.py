from fastapi import APIRouter, Query
from app.schemas.sentinel_processing import SentinelIndicesResponse
from app.services.sentinel_processing_service import sentinel_processing_service

router = APIRouter(prefix="/sentinel", tags=["Sentinel-2 Processing"])


@router.get(
    "/indices",
    response_model=SentinelIndicesResponse,
    summary="Get Sentinel-2 vegetation indices",
    description="Retrieves computed optical indices (NDVI, NDMI, EVI, SAVI) for a given location and date. In the MVP phase, this returns realistic placeholder values if imagery cannot be downloaded."
)
async def get_vegetation_indices(
    latitude: float = Query(..., description="Latitude of the field"),
    longitude: float = Query(..., description="Longitude of the field"),
    observation_date: str = Query(..., description="Date of observation (YYYY-MM-DD)")
) -> SentinelIndicesResponse:
    """Retrieve vegetation indices for the specified parameters."""
    return await sentinel_processing_service.get_vegetation_indices(
        latitude=latitude,
        longitude=longitude,
        observation_date=observation_date
    )
