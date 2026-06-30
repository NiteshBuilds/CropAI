"""
copernicus_service.py
─────────────────────
Service skeleton for the Copernicus Data Space Ecosystem (CDSE).

Responsibilities (future phases):
- Authenticate with CDSE OpenID Connect
- Search the OData catalogue for Sentinel-1 / Sentinel-2 products
- Download product archives and extract bands

Current phase: configuration validation only.
"""

from app.core.api_config import CopernicusConfig, copernicus_config


class CopernicusServiceError(Exception):
    """Raised when the Copernicus service is misconfigured or unavailable."""


class CopernicusService:
    """Facade for all interactions with the Copernicus Data Space Ecosystem."""

    def __init__(self, config: CopernicusConfig = copernicus_config) -> None:
        self._config = config
        self._validate_config()

    # ── Private ───────────────────────────────────────────────────────────────

    def _validate_config(self) -> None:
        """Verify that required configuration fields are present.

        Raises:
            CopernicusServiceError: If any required credential is missing.
        """
        missing: list[str] = []

        if not self._config.username:
            missing.append("COPERNICUS_USERNAME")
        if not self._config.password:
            missing.append("COPERNICUS_PASSWORD")

        if missing:
            raise CopernicusServiceError(
                f"Copernicus service is not configured. "
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
                "catalog_url": self._config.catalog_url,
                "collection_s2": self._config.collection_s2,
                "collection_s1": self._config.collection_s1,
            }
        return {"status": "not_configured", "detail": "Credentials not set"}
