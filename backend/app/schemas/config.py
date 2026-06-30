from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SeasonConfig(BaseModel):
    name: str
    start_month: str
    end_month: str


class CropCalendarEntry(BaseModel):
    sowing: str
    harvesting: str


class AoiPlaceholder(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]


class DistrictConfig(BaseModel):
    """Pydantic model for validating the district configuration JSON."""
    
    district: str
    state: str
    country: str
    season: SeasonConfig
    crop_calendar: Dict[str, CropCalendarEntry]
    satellite_sources: List[str]
    weather_source: str
    aoi_placeholder: AoiPlaceholder
    metadata_version: str
    last_updated: str
