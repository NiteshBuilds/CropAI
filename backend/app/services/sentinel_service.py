"""
sentinel_service.py
────────────────────
Service skeleton for the Sentinel Hub Processing API.

Responsibilities (future phases):
- Obtain OAuth2 access tokens via client-credentials flow
- Execute evalscript-based band requests (NDVI, NDWI, NDMI, EVI, SAR)
- Return processed raster arrays for downstream ML feature extraction

Current phase: configuration validation only.
"""

from app.core.api_config import SentinelHubConfig, sentinel_hub_config


class SentinelServiceError(Exception):
    """Raised when the Sentinel Hub service is misconfigured or unavailable."""


class SentinelService:
    """Facade for all interactions with the Sentinel Hub Processing API."""

    def __init__(self, config: SentinelHubConfig = sentinel_hub_config) -> None:
        self._config = config
        self._validate_config()

    # ── Private ───────────────────────────────────────────────────────────────

    def _validate_config(self) -> None:
        """Verify that both OAuth2 credential fields are present.

        Raises:
            SentinelServiceError: If any required credential is missing.
        """
        missing: list[str] = []

        if not self._config.client_id:
            missing.append("SENTINEL_CLIENT_ID")
        if not self._config.client_secret:
            missing.append("SENTINEL_CLIENT_SECRET")

        if missing:
            raise SentinelServiceError(
                f"Sentinel Hub service is not configured. "
                f"Missing environment variables: {', '.join(missing)}"
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
                "process_endpoint": self._config.process_endpoint,
                "catalog_endpoint": self._config.catalog_endpoint,
            }
        return {"status": "not_configured", "detail": "OAuth2 credentials not set"}
