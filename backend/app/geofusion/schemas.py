from typing import Optional
from pydantic import BaseModel, Field


class OpticalFeatures(BaseModel):
    """Features extracted from Sentinel-2 optical imagery."""
    ndvi: Optional[float] = Field(None, title="Normalized Difference Vegetation Index")
    ndmi: Optional[float] = Field(None, title="Normalized Difference Moisture Index")
    evi: Optional[float] = Field(None, title="Enhanced Vegetation Index")
    savi: Optional[float] = Field(None, title="Soil Adjusted Vegetation Index")
    cloud_cover: Optional[float] = Field(None, title="Cloud Cover Percentage")


class SARFeatures(BaseModel):
    """Features extracted from Sentinel-1 Synthetic Aperture Radar."""
    vv: Optional[float] = Field(None, title="VV Backscatter (dB)")
    vh: Optional[float] = Field(None, title="VH Backscatter (dB)")
    vv_vh_ratio: Optional[float] = Field(None, title="VV/VH Backscatter Ratio")


class WeatherFeatures(BaseModel):
    """Weather variables influencing crop growth and moisture."""
    rainfall: Optional[float] = Field(None, title="Daily Rainfall (mm)")
    temperature: Optional[float] = Field(None, title="Mean Temperature (°C)")
    humidity: Optional[float] = Field(None, title="Relative Humidity (%)")
    wind_speed: Optional[float] = Field(None, title="Wind Speed (m/s)")


class UnifiedFeatureVector(BaseModel):
    """Combined feature vector integrating all data sources for a single observation."""
    observation_date: str
    latitude: float
    longitude: float
    crop: str
    growth_stage: str
    optical_features: OpticalFeatures
    sar_features: SARFeatures
    weather_features: WeatherFeatures
