import json
import logging
from app.geofusion.schemas import (
    OpticalFeatures,
    SARFeatures,
    WeatherFeatures,
    UnifiedFeatureVector,
)

logger = logging.getLogger(__name__)


class FeatureBuilder:
    """
    Constructs unified feature vectors by fusing data from optical, SAR, 
    and weather sources. This serves as the foundation for the AI models.
    """

    def build_empty_vector(self) -> UnifiedFeatureVector:
        """Creates an empty unified feature vector structure."""
        logger.info("Building empty UnifiedFeatureVector template.")
        return UnifiedFeatureVector(
            observation_date="",
            latitude=0.0,
            longitude=0.0,
            crop="",
            growth_stage="",
            optical_features=OpticalFeatures(),
            sar_features=SARFeatures(),
            weather_features=WeatherFeatures(),
        )

    def build_sample_vector(self) -> UnifiedFeatureVector:
        """Creates a sample unified feature vector with realistic placeholder values."""
        logger.info("Building sample UnifiedFeatureVector for Sehore context.")
        return UnifiedFeatureVector(
            observation_date="2025-08-15",
            latitude=23.2,
            longitude=77.0,
            crop="Soybean",
            growth_stage="Pod Formation",
            optical_features=OpticalFeatures(
                ndvi=0.82,
                ndmi=0.55,
                evi=0.68,
                savi=0.45,
                cloud_cover=5.0
            ),
            sar_features=SARFeatures(
                vv=-10.5,
                vh=-16.2,
                vv_vh_ratio=0.65
            ),
            weather_features=WeatherFeatures(
                rainfall=12.5,
                temperature=28.4,
                humidity=75.0,
                wind_speed=14.2
            ),
        )

    def export_json(self, vector: UnifiedFeatureVector) -> str:
        """Exports a unified feature vector to JSON format."""
        return vector.model_dump_json(indent=2)
