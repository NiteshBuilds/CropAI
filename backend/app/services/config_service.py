"""
config_service.py
──────────────────
Service for managing the District Intelligence Module configuration.
Handles loading and validating the JSON configuration for the current operational district.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from app.schemas.config import DistrictConfig, SeasonConfig, CropCalendarEntry
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when the district configuration cannot be loaded or validated."""
    pass


class ConfigService:
    """Service to load, validate, and expose district configuration parameters."""
    
    def __init__(self, config_path: str = "config/district_config.json"):
        # Resolve path relative to the backend root directory (where main.py is located)
        base_dir = Path(__file__).resolve().parents[2]
        self._config_path = base_dir / config_path
        self._config: DistrictConfig = self._load_configuration()
        
    def _load_configuration(self) -> DistrictConfig:
        """
        Loads the JSON file and validates its structure using Pydantic.
        
        Raises:
            ConfigurationError: If the file is missing, invalid JSON, or fails schema validation.
        """
        logger.info(f"Loading District Intelligence Module configuration from {self._config_path}")
        
        try:
            with open(self._config_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                
            config = DistrictConfig(**raw_data)
            logger.info("Successfully validated district configuration.")
            return config
            
        except FileNotFoundError:
            error_msg = f"Configuration file not found at {self._config_path}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except json.JSONDecodeError as exc:
            error_msg = f"Invalid JSON format in configuration file: {exc}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except ValidationError as exc:
            error_msg = f"Configuration structure validation failed: {exc}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except Exception as exc:
            error_msg = f"An unexpected error occurred loading configuration: {exc}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

    # ── Public Getters ────────────────────────────────────────────────────────

    def get_district(self) -> str:
        """Returns the configured district name."""
        return self._config.district

    def get_state(self) -> str:
        """Returns the configured state name."""
        return self._config.state

    def get_season(self) -> SeasonConfig:
        """Returns the season configuration."""
        return self._config.season

    def get_crop_calendar(self) -> Dict[str, CropCalendarEntry]:
        """Returns the crop calendar for all supported crops."""
        return self._config.crop_calendar

    def get_satellite_sources(self) -> List[str]:
        """Returns a list of supported satellite sources."""
        return self._config.satellite_sources

    def get_weather_source(self) -> str:
        """Returns the configured weather data source."""
        return self._config.weather_source

    def get_boundary(self) -> Dict[str, Any]:
        """Returns the AOI (Area of Interest) placeholder polygon."""
        return self._config.aoi_placeholder.model_dump()
        
    def get_full_configuration(self) -> DistrictConfig:
        """Returns the complete configuration object."""
        return self._config


# Module-level singleton
config_service = ConfigService()
