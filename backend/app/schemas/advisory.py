from pydantic import BaseModel, Field


class AdvisoryRequest(BaseModel):
    """Payload for generating a farmer-friendly advisory."""

    crop: str = Field(..., description="Crop name (e.g., Paddy, Soybean, Maize, Pigeon Pea (Tur))")
    growth_stage: str = Field(..., description="Current growth stage (e.g., Vegetative, Flowering)")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")


class AdvisoryResponse(BaseModel):
    """Farmer-friendly advisory synthesised from stress, irrigation and weather inputs."""

    crop: str = Field(..., description="Name of the crop")
    growth_stage: str = Field(..., description="Current growth stage")
    advisory_title: str = Field(..., description="Short, human-readable advisory title")
    advisory_message: str = Field(..., description="Plain-language message for the farmer")
    risk_level: str = Field(..., description="Overall risk level: Low | Medium | High")
    next_action: str = Field(..., description="Recommended immediate action")
    confidence: int = Field(..., description="Confidence score (70–98)")
