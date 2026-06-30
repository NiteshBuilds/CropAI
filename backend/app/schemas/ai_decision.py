from pydantic import BaseModel, Field


class AIDecisionRequest(BaseModel):
    """Input parameters for the Unified AI Decision Engine."""
    crop: str = Field(..., description="Crop name (e.g., Paddy, Soybean, Maize, Pigeon Pea (Tur))")
    growth_stage: str = Field(..., description="Current growth stage (e.g., Vegetative, Flowering)")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")


class AIDecisionResponse(BaseModel):
    """Unified, actionable AI decision synthesised from all engine outputs."""
    crop: str = Field(..., description="Name of the crop")
    growth_stage: str = Field(..., description="Current growth stage")
    farm_status: str = Field(..., description="Overall farm status: Healthy | Monitor Closely | Critical")
    priority_level: str = Field(..., description="Action priority: Low | Medium | High")
    risk_level: str = Field(..., description="Overall risk: Low | Moderate | High")
    recommended_action: str = Field(..., description="Primary recommended action for the farmer")
    expected_outcome: str = Field(..., description="Expected result if action is followed")
    confidence: int = Field(..., description="Confidence score (75–98)")
