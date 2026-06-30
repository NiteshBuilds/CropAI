"""
api_config.py
─────────────
Structured configuration objects for each external data source.

These dataclasses are built from `settings` and are the single source of
truth for base URLs, endpoint paths, and service identifiers consumed by
the service layer.  No credentials are stored here — they remain in settings.
"""

from dataclasses import dataclass

from app.core.settings import settings


@dataclass(frozen=True)
class CopernicusConfig:
    """Configuration for the Copernicus Data Space Ecosystem (CDSE)."""

    auth_url: str = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    catalog_url: str = "https://catalogue.dataspace.copernicus.eu/odata/v1"
    download_url: str = "https://download.dataspace.copernicus.eu"
    collection_s2: str = "SENTINEL-2"
    collection_s1: str = "SENTINEL-1"
    username: str = ""
    password: str = ""

    @classmethod
    def from_settings(cls) -> "CopernicusConfig":
        return cls(
            username=settings.copernicus_username,
            password=settings.copernicus_password,
        )

    @property
    def is_configured(self) -> bool:
        """True only when both credential fields are non-empty."""
        return bool(self.username and self.password)


@dataclass(frozen=True)
class SentinelHubConfig:
    """Configuration for the Sentinel Hub Processing API."""

    base_url: str = "https://services.sentinel-hub.com"
    token_url: str = "https://services.sentinel-hub.com/auth/realms/main/protocol/openid-connect/token"
    process_endpoint: str = "/api/v1/process"
    catalog_endpoint: str = "/api/v1/catalog/1.0.0/search"
    client_id: str = ""
    client_secret: str = ""

    @classmethod
    def from_settings(cls) -> "SentinelHubConfig":
        return cls(
            client_id=settings.sentinel_client_id,
            client_secret=settings.sentinel_client_secret,
        )

    @property
    def is_configured(self) -> bool:
        """True only when both OAuth credential fields are non-empty."""
        return bool(self.client_id and self.client_secret)


@dataclass(frozen=True)
class OpenMeteoConfig:
    """Configuration for the Open-Meteo free weather API (no auth required)."""

    base_url: str = ""
    forecast_endpoint: str = "/forecast"
    historical_endpoint: str = "/archive"

    @classmethod
    def from_settings(cls) -> "OpenMeteoConfig":
        return cls(base_url=settings.open_meteo_base_url)

    @property
    def is_configured(self) -> bool:
        """True when a non-empty base URL is provided."""
        return bool(self.base_url)


# ── Module-level singletons ───────────────────────────────────────────────────
copernicus_config = CopernicusConfig.from_settings()
sentinel_hub_config = SentinelHubConfig.from_settings()
open_meteo_config = OpenMeteoConfig.from_settings()
