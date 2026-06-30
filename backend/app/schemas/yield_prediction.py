from typing import List
from pydantic import BaseModel, Field


class YieldPredictionRequest(BaseModel):
    """Input parameters for the crop yield prediction engine."""
    crop: str = Field(..., description="Crop name (e.g., Paddy, Soybean, Maize, Pigeon Pea (Tur))")
    growth_stage: str = Field(..., description="Current growth stage (e.g., Vegetative, Flowering)")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")


class YieldPredictionResponse(BaseModel):
    """Structured crop yield prediction from the rule-based engine."""
    crop: str = Field(..., description="Name of the crop")
    growth_stage: str = Field(..., description="Current growth stage")
    predicted_yield_ton_per_hectare: float = Field(..., description="Estimated yield in ton/hectare")
    yield_category: str = Field(..., description="Yield category: High | Average | Low")
    confidence: int = Field(..., description="Confidence score (75–98)")
    prediction_reason: List[str] = Field(..., description="Factors driving the yield prediction")
