"""
irrigation_service.py
──────────────────────
Rule-based AI Irrigation Advisory Engine (Phase 9).

Delegates moisture stress analysis to MoistureStressService and weather
observations to WeatherService — no logic is duplicated from those modules.

All irrigation-specific thresholds are centralised here so they can be
replaced by an ML model in later phases without touching any other file.
"""

import logging
import random
from typing import Tuple

from app.geofusion.schemas import WeatherFeatures
from app.schemas.irrigation import IrrigationRequest, IrrigationResponse
from app.schemas.moisture_stress import MoistureStressRequest, MoistureStressResponse
from app.services.moisture_stress_service import moisture_stress_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)


class IrrigationService:
    """
    Generates field-level irrigation recommendations by fusing:
      - Moisture Stress analysis   (via MoistureStressService)
      - Weather observations       (via WeatherService)
      - Growth-stage context       (from request payload)

    Architecture note: this service is intentionally thin.  All spectral
    and meteorological computations live in their own services; only the
    irrigation decision rules are expressed here.
    """

    # ── Irrigation thresholds (ML-replaceable) ────────────────────────────────
    RAINFALL_ADEQUATE_MM: float = 10.0
    RAINFALL_DEFICIENT_MM: float = 5.0
    TEMP_HIGH_C: float = 32.0          # threshold for timing advice
    TEMP_EXTREME_C: float = 35.0       # threshold for High-stress case

    WATER_LOW_STRESS_MM: float = 0.0
    WATER_MODERATE_STRESS_MM: float = 20.0
    WATER_HIGH_STRESS_MM: float = 40.0

    CONFIDENCE_MIN: int = 70
    CONFIDENCE_MAX: int = 98

    async def recommend(self, request: IrrigationRequest) -> IrrigationResponse:
        """
        Entry point for the irrigation advisory engine.

        Steps
        -----
        1. Delegate to MoistureStressService for stress + confidence.
        2. Delegate to WeatherService for rainfall and temperature.
        3. Apply irrigation decision rules.
        4. Return a structured IrrigationResponse.
        """
        logger.info(
            "Generating irrigation recommendation for %s (%s) at %.4f, %.4f on %s",
            request.crop,
            request.growth_stage,
            request.latitude,
            request.longitude,
            request.observation_date,
        )

        # Step 1: Moisture stress analysis (also validates crop + fetches indices)
        stress_result: MoistureStressResponse = await moisture_stress_service.analyze_stress(
            MoistureStressRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # Step 2: Weather observations (reused, not re-fetched from scratch —
        # the weather_service call is idempotent / deterministic for MVP)
        weather: WeatherFeatures = await weather_service.get_weather_observation(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        rainfall: float = weather.rainfall or 0.0
        temperature: float = weather.temperature or 0.0

        # Step 3: Apply decision rules
        stress_level = stress_result.stress_level
        irrigation_required, urgency, water_mm, advisory = self._apply_rules(
            stress_level, rainfall, temperature
        )

        # Step 4: Irrigation timing
        recommended_time = self._recommend_time(temperature)

        # Step 5: Confidence — reuse from moisture stress; clamp to valid range
        confidence = max(
            self.CONFIDENCE_MIN,
            min(self.CONFIDENCE_MAX, stress_result.confidence),
        )

        logger.info(
            "Irrigation advisory complete — stress: %s | irrigation_required: %s | urgency: %s",
            stress_level,
            irrigation_required,
            urgency,
        )

        return IrrigationResponse(
            crop=request.crop,
            growth_stage=request.growth_stage,
            stress_level=stress_level,
            irrigation_required=irrigation_required,
            urgency=urgency,
            recommended_water_mm=water_mm,
            recommended_time=recommended_time,
            advisory=advisory,
            confidence=confidence,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _apply_rules(
        self, stress_level: str, rainfall: float, temperature: float
    ) -> Tuple[bool, str, float, str]:
        """
        Priority-ordered decision rules.
        Returns: (irrigation_required, urgency, water_mm, advisory).
        """

        # CASE 3: High stress — most urgent, check first
        if (
            stress_level == "High"
            and rainfall < self.RAINFALL_DEFICIENT_MM
            and temperature > self.TEMP_EXTREME_C
        ):
            return (
                True,
                "High",
                self.WATER_HIGH_STRESS_MM,
                "Immediate irrigation recommended to prevent crop stress.",
            )

        # CASE 2: Moderate stress with deficient rainfall
        if stress_level == "Moderate" and rainfall < self.RAINFALL_DEFICIENT_MM:
            return (
                True,
                "Medium",
                self.WATER_MODERATE_STRESS_MM,
                "Light irrigation recommended within 24 hours.",
            )

        # CASE 1: Low stress with adequate rainfall
        if stress_level == "Low" and rainfall > self.RAINFALL_ADEQUATE_MM:
            return (
                False,
                "Low",
                self.WATER_LOW_STRESS_MM,
                "No irrigation needed today. Continue monitoring moisture.",
            )

        # Fallback: moderate stress with adequate rainfall — monitor closely
        if stress_level == "Moderate":
            return (
                True,
                "Medium",
                self.WATER_MODERATE_STRESS_MM,
                "Moderate stress detected. Consider light irrigation and monitor closely.",
            )

        # Fallback: high stress but rainfall is borderline — still recommend
        if stress_level == "High":
            return (
                True,
                "High",
                self.WATER_HIGH_STRESS_MM,
                "High stress detected. Immediate irrigation strongly recommended.",
            )

        # Default: insufficient information — conservative advice
        return (
            False,
            "Low",
            self.WATER_LOW_STRESS_MM,
            "Conditions are stable. Continue monitoring crop and soil moisture.",
        )

    def _recommend_time(self, temperature: float) -> str:
        """Return the safest irrigation window based on ambient temperature."""
        if temperature > self.TEMP_HIGH_C:
            return "Early Morning or Evening"
        return "Morning"

    def _build_sample_response(self) -> IrrigationResponse:
        """Return a hardcoded demo response for the /sample endpoint."""
        return IrrigationResponse(
            crop="Paddy",
            growth_stage="Vegetative",
            stress_level="High",
            irrigation_required=True,
            urgency="High",
            recommended_water_mm=40.0,
            recommended_time="Early Morning or Evening",
            advisory="Immediate irrigation recommended to prevent crop stress.",
            confidence=94,
        )


irrigation_service = IrrigationService()
