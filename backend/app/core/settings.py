from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "Crop AI Monitoring System"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False

    # ── Server ────────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── CORS ──────────────────────────────────────────────────────────────────
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Copernicus Data Space Ecosystem ───────────────────────────────────────
    copernicus_username: str = ""
    copernicus_password: str = ""

    # ── Sentinel Hub OAuth 2.0 ────────────────────────────────────────────────
    sentinel_client_id: str = ""
    sentinel_client_secret: str = ""

    # ── Open-Meteo Weather API ────────────────────────────────────────────────
    open_meteo_base_url: str = ""

    # ── Geospatial Defaults ───────────────────────────────────────────────────
    default_latitude: float | None = None
    default_longitude: float | None = None
    default_aoi_radius_km: float = 5.0


settings = Settings()
