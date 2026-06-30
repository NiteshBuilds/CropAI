"""
advisory_service.py
────────────────────
Phase 10 — Farmer Advisory Engine.

Orchestrates MoistureStressService, IrrigationService, and WeatherService
to produce a single, farmer-friendly recommendation.

All advisory rules live here so they can be swapped for an ML model later
without touching any other file in the project.
"""

import logging
from typing import Tuple

from app.geofusion.schemas import WeatherFeatures
from app.schemas.advisory import AdvisoryRequest, AdvisoryResponse
from app.schemas.irrigation import IrrigationRequest, IrrigationResponse
from app.schemas.moisture_stress import MoistureStressRequest, MoistureStressResponse
from app.services.irrigation_service import irrigation_service
from app.services.moisture_stress_service import moisture_stress_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)


class AdvisoryService:
    """
    Rule-based farmer advisory engine.

    Composes results from the moisture-stress and irrigation layers,
    supplements them with live weather data, then selects a human-readable
    advisory from a priority-ordered rule table.
    """

    # ── Thresholds (ML-replaceable) ───────────────────────────────────────────
    TEMP_EXTREME_C: float = 35.0
    RAINFALL_ADEQUATE_MM: float = 10.0

    async def generate(self, request: AdvisoryRequest) -> AdvisoryResponse:
        """
        Full advisory pipeline.

        1. Moisture stress analysis  (stress_level, confidence)
        2. Irrigation recommendation (irrigation_required, urgency)
        3. Weather observation        (temperature, rainfall)
        4. Rule engine               → advisory_title / message / risk / action
        """
        logger.info(
            "Generating farmer advisory for %s (%s) at %.4f, %.4f on %s",
            request.crop,
            request.growth_stage,
            request.latitude,
            request.longitude,
            request.observation_date,
        )

        # Step 1 — Moisture stress
        stress: MoistureStressResponse = await moisture_stress_service.analyze_stress(
            MoistureStressRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # Step 2 — Irrigation recommendation
        irrigation: IrrigationResponse = await irrigation_service.recommend(
            IrrigationRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # Step 3 — Weather (deterministic seed — no redundant network call)
        weather: WeatherFeatures = await weather_service.get_weather_observation(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        temperature: float = weather.temperature or 0.0
        rainfall: float = weather.rainfall or 0.0

        # Step 4 — Select advisory
        title, message, risk_level, next_action = self._select_advisory(
            stress_level=stress.stress_level,
            irrigation_required=irrigation.irrigation_required,
            temperature=temperature,
            rainfall=rainfall,
        )

        # Confidence is inherited from the moisture-stress engine (already 70–98 range)
        confidence = max(70, min(98, stress.confidence))

        logger.info(
            "Advisory generated — risk: %s | title: %s | confidence: %d",
            risk_level,
            title,
            confidence,
        )

        return AdvisoryResponse(
            crop=request.crop,
            growth_stage=request.growth_stage,
            advisory_title=title,
            advisory_message=message,
            risk_level=risk_level,
            next_action=next_action,
            confidence=confidence,
        )

    # ── Rule engine ───────────────────────────────────────────────────────────

    def _select_advisory(
        self,
        stress_level: str,
        irrigation_required: bool,
        temperature: float,
        rainfall: float,
    ) -> Tuple[str, str, str, str]:
        """
        Priority-ordered advisory rules.
        Returns (title, message, risk_level, next_action).
        """

        # CASE 3 — High stress + extreme heat (most critical; evaluated first)
        if stress_level == "High" and temperature > self.TEMP_EXTREME_C:
            return (
                "High Moisture Stress Alert",
                (
                    "Immediate irrigation is recommended to prevent yield loss "
                    "due to moisture stress and high temperatures."
                ),
                "High",
                "Irrigate immediately and monitor field conditions daily.",
            )

        # CASE 2 — Moderate stress with irrigation required
        if stress_level == "Moderate" and irrigation_required:
            return (
                "Moderate Moisture Stress",
                "Light irrigation is recommended within 24 hours to maintain healthy crop growth.",
                "Medium",
                "Apply recommended irrigation and reassess moisture after 2 days.",
            )

        # CASE 1 — Low stress, no irrigation needed, rain expected
        if (
            stress_level == "Low"
            and not irrigation_required
            and rainfall > self.RAINFALL_ADEQUATE_MM
        ):
            return (
                "Healthy Crop Condition",
                (
                    "No irrigation needed today. Rainfall is expected and "
                    "crop moisture appears adequate."
                ),
                "Low",
                "Continue monitoring over the next 3 days.",
            )

        # Fallback: High stress without extreme temperatures
        if stress_level == "High":
            return (
                "High Moisture Stress Alert",
                "Crop is under significant moisture stress. Irrigation is strongly recommended.",
                "High",
                "Irrigate immediately and monitor field conditions daily.",
            )

        # Fallback: Low/Moderate stress, irrigation not explicitly required
        if stress_level == "Low":
            return (
                "Stable Crop Condition",
                "Crop moisture levels appear stable. No immediate action required.",
                "Low",
                "Continue routine monitoring and check again in 3 days.",
            )

        # Final fallback: generic moderate advisory
        return (
            "Moderate Crop Condition",
            "Some moisture variability detected. Consider light irrigation as a precaution.",
            "Medium",
            "Review soil moisture and weather forecast before the next irrigation cycle.",
        )

    def build_sample_response(self) -> AdvisoryResponse:
        """Return a hardcoded demo advisory for the /sample endpoint."""
        return AdvisoryResponse(
            crop="Paddy",
            growth_stage="Vegetative",
            advisory_title="Moderate Moisture Stress",
            advisory_message=(
                "Light irrigation is recommended within 24 hours "
                "to maintain healthy crop growth."
            ),
            risk_level="Medium",
            next_action="Apply recommended irrigation and reassess moisture after 2 days.",
            confidence=95,
        )


advisory_service = AdvisoryService()
