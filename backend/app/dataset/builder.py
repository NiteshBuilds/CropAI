import json
from typing import Dict, Any

from app.dataset.schemas import (
    TemporalDataset, 
    TemporalObservation, 
    WeatherObservation, 
    SatelliteObservation
)


class DatasetBuilder:
    """
    Builder class to construct a temporal spectral dataset.
    This creates the foundational structure that will later be populated 
    with real data from satellite APIs and weather services.
    """

    def __init__(self) -> None:
        self.dataset = self.create_empty_dataset()

    def create_empty_dataset(self) -> TemporalDataset:
        """Initializes a new empty dataset for the active district (Sehore)."""
        return TemporalDataset(
            district="Sehore",
            state="Madhya Pradesh",
            country="India",
            season="Kharif",
            observations=[]
        )

    def create_observation(
        self, 
        date: str, 
        crop_name: str, 
        growth_stage: str, 
        latitude: float, 
        longitude: float,
        weather: WeatherObservation,
        satellite_features: SatelliteObservation,
        metadata: Dict[str, Any] = None
    ) -> TemporalObservation:
        """Creates a single temporal observation with the provided data."""
        return TemporalObservation(
            date=date,
            crop_name=crop_name,
            growth_stage=growth_stage,
            latitude=latitude,
            longitude=longitude,
            weather=weather,
            satellite_features=satellite_features,
            metadata=metadata or {}
        )

    def add_observation(self, observation: TemporalObservation) -> None:
        """Adds an observation to the current dataset."""
        self.dataset.observations.append(observation)

    def export_json(self) -> str:
        """Exports the complete temporal dataset as a JSON string."""
        return self.dataset.model_dump_json(indent=2)
