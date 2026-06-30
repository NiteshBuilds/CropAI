"""
yield_prediction_service.py
────────────────────────────
Phase 12 — Crop Yield Prediction Engine.

Uses Sentinel-2 indices, moisture stress analysis, and weather data to
estimate expected crop yield via a rule-based engine.

All thresholds and crop baselines live here so they can be replaced with
a trained ML model (e.g., XGBoost regressor) in a later phase without
touching any other file.
"""

import logging
from typing import List, Tuple

from app.schemas.moisture_stress import MoistureStressRequest
from app.schemas.yield_prediction import YieldPredictionRequest, YieldPredictionResponse
from app.services.moisture_stress_service import moisture_stress_service
from app.services.sentinel_processing_service import sentinel_processing_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)


class YieldPredictionService:
    """
    Rule-based crop yield prediction engine.

    Inputs are sourced from the existing service layer — no logic is duplicated.
    """

    # ── Crop baseline yields (ton/hectare) — ML-replaceable ──────────────────
    CROP_BASELINES: dict[str, float] = {
        "Paddy": 4.5,
        "Soybean": 2.0,
        "Maize": 5.0,
        "Pigeon Pea (Tur)": 1.5,
    }

    # ── NDVI thresholds ───────────────────────────────────────────────────────
    NDVI_HIGH: float = 0.70
    NDVI_LOW: float = 0.50

    # ── Rainfall threshold ────────────────────────────────────────────────────
    RAINFALL_ADEQUATE_MM: float = 10.0

    # ── Yield adjustment factors ──────────────────────────────────────────────
    HIGH_YIELD_FACTOR: float = 1.20    # baseline + 20 %
    LOW_YIELD_FACTOR: float = 0.75     # baseline − 25 %

    # ── Confidence range ──────────────────────────────────────────────────────
    CONFIDENCE_MIN: int = 75
    CONFIDENCE_MAX: int = 98

    async def predict(self, request: YieldPredictionRequest) -> YieldPredictionResponse:
        """
        Full yield prediction pipeline.

        1. Retrieve Sentinel-2 vegetation indices.
        2. Run moisture stress analysis.
        3. Fetch weather observations.
        4. Apply rule-based yield engine.
        """
        crop = request.crop
        if crop not in self.CROP_BASELINES:
            supported = ", ".join(sorted(self.CROP_BASELINES.keys()))
            raise ValueError(
                f"Unsupported crop '{crop}'. Supported crops: {supported}"
            )

        logger.info(
            "Predicting yield for %s (%s) at %.4f, %.4f on %s",
            crop,
            request.growth_stage,
            request.latitude,
            request.longitude,
            request.observation_date,
        )

        # 1 — Sentinel-2 indices
        indices = await sentinel_processing_service.get_vegetation_indices(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        # 2 — Moisture stress
        stress = await moisture_stress_service.analyze_stress(
            MoistureStressRequest(
                crop=crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # 3 — Weather
        weather = await weather_service.get_weather_observation(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        rainfall: float = weather.rainfall or 0.0
        ndvi: float = indices.ndvi

        # 4 — Apply rules
        baseline = self.CROP_BASELINES[crop]
        yield_category, predicted_yield, reasons = self._apply_rules(
            ndvi=ndvi,
            stress_level=stress.stress_level,
            rainfall=rainfall,
            baseline=baseline,
        )

        # Confidence: blend stress engine confidence with cloud-cover penalty
        confidence = self._compute_confidence(
            stress_confidence=stress.confidence,
            cloud_cover=indices.cloud_cover,
        )

        logger.info(
            "Yield prediction — category: %s | %.2f t/ha | confidence: %d%%",
            yield_category,
            predicted_yield,
            confidence,
        )

        return YieldPredictionResponse(
            crop=crop,
            growth_stage=request.growth_stage,
            predicted_yield_ton_per_hectare=round(predicted_yield, 2),
            yield_category=yield_category,
            confidence=confidence,
            prediction_reason=reasons,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _apply_rules(
        self,
        ndvi: float,
        stress_level: str,
        rainfall: float,
        baseline: float,
    ) -> Tuple[str, float, List[str]]:
        """
        Priority-ordered yield rules.
        Returns (yield_category, predicted_yield_t_ha, reasons).
        """
        reasons: List[str] = []

        # HIGH YIELD — evaluated first (most favourable)
        if ndvi > self.NDVI_HIGH and stress_level == "Low" and rainfall > self.RAINFALL_ADEQUATE_MM:
            reasons.append("Healthy NDVI")
            reasons.append("Low Moisture Stress")
            reasons.append("Adequate Rainfall")
            return "High", baseline * self.HIGH_YIELD_FACTOR, reasons

        # LOW YIELD — evaluated second (most critical)
        if ndvi < self.NDVI_LOW and stress_level == "High":
            reasons.append("Poor NDVI")
            reasons.append("High Moisture Stress")
            if rainfall < self.RAINFALL_ADEQUATE_MM:
                reasons.append("Insufficient Rainfall")
            return "Low", baseline * self.LOW_YIELD_FACTOR, reasons

        # AVERAGE YIELD — broad middle band
        if self.NDVI_LOW <= ndvi <= self.NDVI_HIGH or stress_level == "Moderate":
            if self.NDVI_LOW <= ndvi <= self.NDVI_HIGH:
                reasons.append("Moderate NDVI")
            if stress_level == "Moderate":
                reasons.append("Moderate Moisture Stress")
            if rainfall < self.RAINFALL_ADEQUATE_MM:
                reasons.append("Below-average Rainfall")
            return "Average", baseline, reasons

        # Fallback: high NDVI but other factors limiting
        if ndvi > self.NDVI_HIGH:
            reasons.append("Healthy NDVI")
            if stress_level != "Low":
                reasons.append(f"{stress_level} Moisture Stress limiting potential")
            return "Average", baseline, reasons

        # Final fallback
        reasons.append("Insufficient data for confident prediction")
        return "Average", baseline, reasons

    def _compute_confidence(self, stress_confidence: int, cloud_cover: float) -> int:
        """
        Derive confidence (75–98 %) from the stress engine score with a
        cloud-cover penalty applied for reduced spectral reliability.
        """
        # Re-scale from stress engine range (70–98) to yield range (75–98)
        confidence = max(self.CONFIDENCE_MIN, min(self.CONFIDENCE_MAX, stress_confidence))

        # Cloud-cover penalty: −5 per 10 % cloud cover over 15 %
        if cloud_cover > 15.0:
            penalty = int((cloud_cover - 15.0) / 10.0) * 5
            confidence = max(self.CONFIDENCE_MIN, confidence - penalty)

        return confidence

    def build_sample_response(self) -> YieldPredictionResponse:
        """Return a hardcoded demo prediction for the /sample endpoint."""
        return YieldPredictionResponse(
            crop="Paddy",
            growth_stage="Vegetative",
            predicted_yield_ton_per_hectare=5.4,
            yield_category="High",
            confidence=92,
            prediction_reason=["Healthy NDVI", "Low Moisture Stress", "Adequate Rainfall"],
        )


yield_prediction_service = YieldPredictionService()
