"""
dashboard_service.py
─────────────────────
Phase 11 — Hackathon Demo Dashboard.

Aggregates outputs from all previous AI engines into a single, flat response
that the frontend (or demo presenter) can consume with one API call.

No new AI logic is introduced here — this is pure orchestration.
"""

import logging

from app.schemas.advisory import AdvisoryRequest
from app.schemas.dashboard import (
    AdvisorySummary,
    DashboardRequest,
    DashboardResponse,
    IrrigationSummary,
    MoistureStressSummary,
    SatelliteIndicesSummary,
)
from app.schemas.irrigation import IrrigationRequest
from app.schemas.moisture_stress import MoistureStressRequest
from app.services.advisory_service import advisory_service
from app.services.irrigation_service import irrigation_service
from app.services.moisture_stress_service import moisture_stress_service
from app.services.sentinel_processing_service import sentinel_processing_service

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Orchestrates all AI engine calls and shapes their outputs into a single
    dashboard-ready payload. Call order is sequential so that each result
    can inform logging; the engines are independently idempotent.
    """

    async def get_summary(self, request: DashboardRequest) -> DashboardResponse:
        """
        Full aggregation pipeline.

        1. Sentinel-2 vegetation indices
        2. Moisture stress analysis
        3. Irrigation recommendation
        4. Farmer advisory
        """
        logger.info(
            "Dashboard summary requested for %s (%s) at %.4f, %.4f on %s",
            request.crop,
            request.growth_stage,
            request.latitude,
            request.longitude,
            request.observation_date,
        )

        # 1 — Satellite indices
        indices = await sentinel_processing_service.get_vegetation_indices(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        # 2 — Moisture stress
        stress = await moisture_stress_service.analyze_stress(
            MoistureStressRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # 3 — Irrigation recommendation
        irrigation = await irrigation_service.recommend(
            IrrigationRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # 4 — Farmer advisory
        advisory = await advisory_service.generate(
            AdvisoryRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        logger.info(
            "Dashboard summary complete — stress: %s | urgency: %s | risk: %s",
            stress.stress_level,
            irrigation.urgency,
            advisory.risk_level,
        )

        return DashboardResponse(
            crop=request.crop,
            growth_stage=request.growth_stage,
            satellite_indices=SatelliteIndicesSummary(
                ndvi=indices.ndvi,
                ndmi=indices.ndmi,
                evi=indices.evi,
                savi=indices.savi,
                cloud_cover=indices.cloud_cover,
            ),
            moisture_stress=MoistureStressSummary(
                stress_level=stress.stress_level,
                confidence=stress.confidence,
            ),
            irrigation=IrrigationSummary(
                irrigation_required=irrigation.irrigation_required,
                recommended_water_mm=irrigation.recommended_water_mm,
                urgency=irrigation.urgency,
            ),
            advisory=AdvisorySummary(
                title=advisory.advisory_title,
                message=advisory.advisory_message,
            ),
        )

    def build_sample_response(self) -> DashboardResponse:
        """Return a hardcoded demo payload for the /sample endpoint."""
        return DashboardResponse(
            crop="Paddy",
            growth_stage="Vegetative",
            satellite_indices=SatelliteIndicesSummary(
                ndvi=0.72,
                ndmi=0.31,
                evi=0.58,
                savi=0.55,
                cloud_cover=12.0,
            ),
            moisture_stress=MoistureStressSummary(
                stress_level="Moderate",
                confidence=91,
            ),
            irrigation=IrrigationSummary(
                irrigation_required=True,
                recommended_water_mm=20.0,
                urgency="Medium",
            ),
            advisory=AdvisorySummary(
                title="Moderate Moisture Stress",
                message="Light irrigation recommended within 24 hours.",
            ),
        )


dashboard_service = DashboardService()
