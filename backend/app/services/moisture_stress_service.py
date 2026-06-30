import logging
from typing import List, Tuple

from app.geofusion.schemas import WeatherFeatures
from app.schemas.moisture_stress import MoistureStressRequest, MoistureStressResponse
from app.schemas.sentinel_processing import SentinelIndicesResponse
from app.services.config_service import config_service
from app.services.sentinel_processing_service import sentinel_processing_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)


class MoistureStressService:
    """
    Rule-based MVP engine for estimating crop moisture stress.
    Fuses vegetation indices (Sentinel-2) with weather data (Open-Meteo).
    Threshold constants can later be replaced by an ML model.
    """

    # ── Rule thresholds (replaceable by ML in later phases) ─────────────────
    NDMI_LOW_STRESS_MIN = 0.45
    NDMI_MODERATE_MIN = 0.20
    NDMI_MODERATE_MAX = 0.45
    NDMI_HIGH_STRESS_MAX = 0.20

    RAINFALL_LOW_STRESS_MIN_MM = 10.0
    RAINFALL_HIGH_STRESS_MAX_MM = 5.0

    TEMPERATURE_MODERATE_STRESS_C = 34.0
    TEMPERATURE_HIGH_STRESS_C = 35.0

    CLOUD_COVER_CONFIDENCE_THRESHOLD = 10.0
    CONFIDENCE_MIN = 70
    CONFIDENCE_MAX = 98

    SUPPORTED_CROPS = frozenset(config_service.get_crop_calendar().keys())

    async def analyze_stress(self, request: MoistureStressRequest) -> MoistureStressResponse:
        """Calculate moisture stress from satellite indices and weather observations."""
        if request.crop not in self.SUPPORTED_CROPS:
            supported = ", ".join(sorted(self.SUPPORTED_CROPS))
            raise ValueError(
                f"Unsupported crop '{request.crop}'. Supported crops: {supported}"
            )

        logger.info(
            "Analyzing moisture stress for %s (%s) at %s, %s on %s",
            request.crop,
            request.growth_stage,
            request.latitude,
            request.longitude,
            request.observation_date,
        )

        indices = await sentinel_processing_service.get_vegetation_indices(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )
        weather = await weather_service.get_weather_observation(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        stress_level, soil_moisture, reasons = self._evaluate_rules(indices, weather)
        confidence = self._compute_confidence(indices, weather)

        return MoistureStressResponse(
            crop=request.crop,
            growth_stage=request.growth_stage,
            stress_level=stress_level,
            soil_moisture=soil_moisture,
            confidence=confidence,
            reason=reasons,
        )

    def build_sample_response(self) -> MoistureStressResponse:
        """Return a realistic sample assessment for API documentation and demos."""
        return MoistureStressResponse(
            crop="Paddy",
            growth_stage="Vegetative",
            stress_level="Moderate",
            soil_moisture="Low",
            confidence=91,
            reason=["Low NDMI", "High Temperature", "Low Rainfall"],
        )

    def _evaluate_rules(
        self,
        indices: SentinelIndicesResponse,
        weather: WeatherFeatures,
    ) -> Tuple[str, str, List[str]]:
        """Apply priority-ordered moisture stress rules and collect trigger reasons."""
        ndmi = indices.ndmi
        rainfall = weather.rainfall or 0.0
        temperature = weather.temperature or 0.0
        reasons: List[str] = []

        is_high_ndmi = ndmi > self.NDMI_LOW_STRESS_MIN
        is_moderate_ndmi = self.NDMI_MODERATE_MIN <= ndmi <= self.NDMI_MODERATE_MAX
        is_low_ndmi = ndmi < self.NDMI_HIGH_STRESS_MAX
        is_adequate_rainfall = rainfall > self.RAINFALL_LOW_STRESS_MIN_MM
        is_low_rainfall = rainfall < self.RAINFALL_HIGH_STRESS_MAX_MM
        is_high_temperature = temperature > self.TEMPERATURE_MODERATE_STRESS_C
        is_extreme_temperature = temperature > self.TEMPERATURE_HIGH_STRESS_C

        if is_low_ndmi and is_low_rainfall and is_extreme_temperature:
            if is_low_ndmi:
                reasons.append("Low NDMI")
            if is_low_rainfall:
                reasons.append("Low Rainfall")
            if is_extreme_temperature:
                reasons.append("High Temperature")
            return "High", "Low", reasons

        if is_high_ndmi and is_adequate_rainfall:
            reasons.append("High NDMI")
            reasons.append("Adequate Rainfall")
            return "Low", "High", reasons

        if is_moderate_ndmi or is_high_temperature:
            if is_moderate_ndmi:
                reasons.append("Moderate NDMI")
            elif is_low_ndmi:
                reasons.append("Low NDMI")
            if is_high_temperature:
                reasons.append("High Temperature")
            if is_low_rainfall and "Low Rainfall" not in reasons:
                reasons.append("Low Rainfall")
            return "Moderate", "Medium", reasons

        if is_low_ndmi:
            reasons.append("Low NDMI")
        elif is_high_ndmi:
            reasons.append("High NDMI")
        if is_low_rainfall:
            reasons.append("Low Rainfall")
        elif is_adequate_rainfall:
            reasons.append("Adequate Rainfall")
        if is_high_temperature:
            reasons.append("High Temperature")

        if not reasons:
            reasons.append("Stable vegetation and weather conditions")

        return "Moderate", "Medium", reasons

    def _compute_confidence(
        self,
        indices: SentinelIndicesResponse,
        weather: WeatherFeatures,
    ) -> int:
        """Derive confidence (70–98%) from data completeness and cloud cover."""
        completeness_fields = [
            indices.ndvi,
            indices.ndmi,
            indices.evi,
            indices.savi,
            indices.cloud_cover,
            weather.temperature,
            weather.humidity,
            weather.rainfall,
            weather.wind_speed,
        ]
        present_count = sum(value is not None for value in completeness_fields)
        total_count = len(completeness_fields)

        confidence = self.CONFIDENCE_MIN + int(
            (present_count / total_count) * (self.CONFIDENCE_MAX - self.CONFIDENCE_MIN)
        )

        if indices.cloud_cover is not None and indices.cloud_cover > self.CLOUD_COVER_CONFIDENCE_THRESHOLD:
            confidence -= 8

        return max(self.CONFIDENCE_MIN, min(self.CONFIDENCE_MAX, confidence))


moisture_stress_service = MoistureStressService()
