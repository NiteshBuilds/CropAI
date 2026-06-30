"""
weather_service.py
──────────────────
Service skeleton for the Open-Meteo weather API.

Open-Meteo is a free, open-source weather API that requires no API key.
Only a valid base URL is needed.

Responsibilities (future phases):
- Fetch hourly / daily forecast for a given lat/lon
- Retrieve historical reanalysis data (ERA5) for crop-stress correlation
- Supply evapotranspiration (ET₀) estimates for irrigation advisory

Current phase: configuration validation plus MVP placeholder observations.
"""

import logging
import random

from app.core.api_config import OpenMeteoConfig, open_meteo_config
from app.geofusion.schemas import WeatherFeatures

logger = logging.getLogger(__name__)


class WeatherServiceError(Exception):
    """Raised when the weather service is misconfigured or unavailable."""


class WeatherService:
    """Facade for all interactions with the Open-Meteo weather API."""

    def __init__(self, config: OpenMeteoConfig = open_meteo_config) -> None:
        self._config = config
        self._validate_config()

    # ── Private ───────────────────────────────────────────────────────────────

    def _validate_config(self) -> None:
        """Verify that the base URL is present.

        Raises:
            WeatherServiceError: If OPEN_METEO_BASE_URL is not set.
        """
        if not self._config.base_url:
            raise WeatherServiceError(
                "Weather service is not configured. "
                "Missing environment variable: OPEN_METEO_BASE_URL"
            )

    # ── Public ────────────────────────────────────────────────────────────────

    def health_check(self) -> dict[str, str]:
        """Return configuration status without making any network call.

        Returns:
            A dict with 'status' and 'detail' keys.
        """
        if self._config.is_configured:
            return {
                "status": "configured",
                "base_url": self._config.base_url,
                "forecast_endpoint": self._config.forecast_endpoint,
                "historical_endpoint": self._config.historical_endpoint,
            }
        return {"status": "not_configured", "detail": "OPEN_METEO_BASE_URL not set"}

    async def get_weather_observation(
        self, latitude: float, longitude: float, observation_date: str
    ) -> WeatherFeatures:
        """Return weather variables for a location and date.

        MVP phase: returns deterministic placeholder values seeded by inputs.
        Later phases will call the Open-Meteo forecast / archive endpoints.
        """
        logger.info(
            "Fetching weather observation for %s, %s on %s",
            latitude,
            longitude,
            observation_date,
        )

        if not self._config.is_configured:
            logger.warning(
                "Open-Meteo is not configured. Falling back to offline placeholders."
            )

        seed_val = hash(f"weather_{latitude}_{longitude}_{observation_date}")
        random.seed(seed_val)

        return WeatherFeatures(
            rainfall=round(random.uniform(0.0, 25.0), 1),
            temperature=round(random.uniform(22.0, 40.0), 1),
            humidity=round(random.uniform(40.0, 95.0), 1),
            wind_speed=round(random.uniform(2.0, 15.0), 1),
        )


def _create_weather_service() -> WeatherService:
    """Instantiate the weather service, using a default base URL for local MVP runs."""
    try:
        return WeatherService()
    except WeatherServiceError:
        return WeatherService(
            config=OpenMeteoConfig(base_url="https://api.open-meteo.com/v1")
        )


weather_service = _create_weather_service()
