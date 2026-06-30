from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date


class WeatherObservation(BaseModel):
    """Placeholders for weather data."""
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None


class SatelliteObservation(BaseModel):
    """Placeholders for satellite-derived spectral indices and SAR backscatter."""
    ndvi: Optional[float] = Field(None, title="NDVI")
    ndmi: Optional[float] = Field(None, title="NDMI")
    evi: Optional[float] = Field(None, title="EVI")
    vv: Optional[float] = Field(None, title="Sentinel-1 VV Backscatter")
    vh: Optional[float] = Field(None, title="Sentinel-1 VH Backscatter")
    cloud_percentage: Optional[float] = Field(None, ge=0, le=100)


class TemporalObservation(BaseModel):
    """Combines weather, satellite, and crop metadata for a specific date."""
    date: str
    crop_name: str
    growth_stage: str
    latitude: float
    longitude: float
    weather: WeatherObservation
    satellite_features: SatelliteObservation
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemporalDataset(BaseModel):
    """A collection of temporal observations for a field or region."""
    district: str = "Sehore"
    state: str = "Madhya Pradesh"
    country: str = "India"
    season: str = "Kharif"
    observations: List[TemporalObservation] = Field(default_factory=list)
