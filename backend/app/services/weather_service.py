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

Current phase: configuration validation only.
"""

from app.core.api_config import OpenMeteoConfig, open_meteo_config


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
