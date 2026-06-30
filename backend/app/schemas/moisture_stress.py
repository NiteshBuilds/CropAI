from typing import List
from pydantic import BaseModel, Field


class MoistureStressRequest(BaseModel):
    """Payload to request moisture stress analysis."""
    crop: str = Field(..., description="Name of the crop (e.g., Paddy, Soybean)")
    growth_stage: str = Field(..., description="Current growth stage (e.g., Vegetative, Flowering)")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")


class MoistureStressResponse(BaseModel):
    """Result of the moisture stress detection engine."""
    crop: str = Field(..., description="Name of the crop")
    growth_stage: str = Field(..., description="Current growth stage")
    stress_level: str = Field(..., description="Computed moisture stress level (Low, Moderate, High)")
    soil_moisture: str = Field(..., description="Estimated soil moisture state")
    confidence: int = Field(..., description="Confidence score (percentage)")
    reason: List[str] = Field(..., description="Factors driving the stress determination")
