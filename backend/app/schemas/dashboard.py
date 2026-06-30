from pydantic import BaseModel, Field


class DashboardRequest(BaseModel):
    """Input parameters for the full dashboard aggregation pipeline."""
    crop: str = Field(..., description="Crop name (e.g., Paddy, Soybean, Maize, Pigeon Pea (Tur))")
    growth_stage: str = Field(..., description="Current growth stage (e.g., Vegetative, Flowering)")
    latitude: float = Field(..., description="Latitude of the field")
    longitude: float = Field(..., description="Longitude of the field")
    observation_date: str = Field(..., description="Observation date (YYYY-MM-DD)")


class SatelliteIndicesSummary(BaseModel):
    """Compact satellite indices for the dashboard."""
    ndvi: float
    ndmi: float
    evi: float
    savi: float
    cloud_cover: float


class MoistureStressSummary(BaseModel):
    """Compact moisture stress output for the dashboard."""
    stress_level: str
    confidence: int


class IrrigationSummary(BaseModel):
    """Compact irrigation recommendation for the dashboard."""
    irrigation_required: bool
    recommended_water_mm: float
    urgency: str


class AdvisorySummary(BaseModel):
    """Compact farmer advisory for the dashboard."""
    title: str
    message: str


class DashboardResponse(BaseModel):
    """Aggregated dashboard response combining all AI engine outputs."""
    crop: str
    growth_stage: str
    satellite_indices: SatelliteIndicesSummary
    moisture_stress: MoistureStressSummary
    irrigation: IrrigationSummary
    advisory: AdvisorySummary
