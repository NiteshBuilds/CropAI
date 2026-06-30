from pydantic import BaseModel, Field


class IrrigationRequest(BaseModel):
    """Payload for an irrigation recommendation request."""

    crop: str = Field(..., description="Crop name (e.g., Paddy, Soybean, Maize, Pigeon Pea (Tur))")
    growth_stage: str = Field(..., description="Current growth stage (e.g., Vegetative, Flowering)")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")


class IrrigationResponse(BaseModel):
    """Complete irrigation recommendation produced by the advisory engine."""

    crop: str = Field(..., description="Name of the crop")
    growth_stage: str = Field(..., description="Current growth stage")
    stress_level: str = Field(..., description="Moisture stress level from the stress engine")
    irrigation_required: bool = Field(..., description="Whether irrigation is recommended")
    urgency: str = Field(..., description="Urgency level: Low | Medium | High")
    recommended_water_mm: float = Field(..., description="Recommended irrigation amount in mm")
    recommended_time: str = Field(..., description="Best time to irrigate")
    advisory: str = Field(..., description="Plain-language advisory message for the farmer")
    confidence: int = Field(..., description="Confidence score (70–98)")
