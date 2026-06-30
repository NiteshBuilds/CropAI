from pydantic import BaseModel, Field


class SentinelIndicesResponse(BaseModel):
    """Response model for Sentinel-2 vegetation indices."""
    observation_date: str = Field(..., description="Date of the satellite observation")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    ndvi: float = Field(..., description="Normalized Difference Vegetation Index")
    ndmi: float = Field(..., description="Normalized Difference Moisture Index")
    evi: float = Field(..., description="Enhanced Vegetation Index")
    savi: float = Field(..., description="Soil Adjusted Vegetation Index")
    cloud_cover: float = Field(..., description="Cloud cover percentage over the area")
