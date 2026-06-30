from fastapi import APIRouter
from app.dataset.schemas import TemporalDataset, WeatherObservation, SatelliteObservation
from app.dataset.builder import DatasetBuilder
import json

router = APIRouter(prefix="/dataset", tags=["Dataset"])


@router.get(
    "/template",
    response_model=TemporalDataset,
    summary="Get empty dataset template",
    description="Returns an empty TemporalDataset structure configured for the active district (Sehore).",
)
async def get_template() -> TemporalDataset:
    """Return an empty dataset template."""
    builder = DatasetBuilder()
    return builder.dataset


@router.get(
    "/sample",
    response_model=TemporalDataset,
    summary="Get sample dataset",
    description="Returns a sample TemporalDataset with 5 realistic dummy observations.",
)
async def get_sample() -> TemporalDataset:
    """Return a small sample dataset with 5 dummy observations."""
    builder = DatasetBuilder()
    
    # Sehore District coordinates
    lat = 23.2
    lon = 77.0

    # Observation 1: Soybean - Sowing
    obs1 = builder.create_observation(
        date="2025-06-20",
        crop_name="Soybean",
        growth_stage="Sowing",
        latitude=lat,
        longitude=lon,
        weather=WeatherObservation(temperature=32.5, rainfall=15.0, humidity=65.0, wind_speed=12.5),
        satellite_features=SatelliteObservation(ndvi=0.15, ndmi=0.10, evi=0.12, vv=-14.5, vh=-22.3, cloud_percentage=5.0)
    )
    
    # Observation 2: Maize - Vegetative
    obs2 = builder.create_observation(
        date="2025-07-05",
        crop_name="Maize",
        growth_stage="Vegetative",
        latitude=lat,
        longitude=lon,
        weather=WeatherObservation(temperature=29.0, rainfall=45.0, humidity=80.0, wind_speed=15.0),
        satellite_features=SatelliteObservation(ndvi=0.45, ndmi=0.35, evi=0.40, vv=-12.0, vh=-18.5, cloud_percentage=15.0)
    )

    # Observation 3: Soybean - Flowering
    obs3 = builder.create_observation(
        date="2025-07-22",
        crop_name="Soybean",
        growth_stage="Flowering",
        latitude=lat,
        longitude=lon,
        weather=WeatherObservation(temperature=27.5, rainfall=60.0, humidity=85.0, wind_speed=10.0),
        satellite_features=SatelliteObservation(ndvi=0.75, ndmi=0.55, evi=0.65, vv=-10.5, vh=-16.0, cloud_percentage=20.0)
    )

    # Observation 4: Maize - Pod Formation (using equivalent stage for maize context or general mapping)
    obs4 = builder.create_observation(
        date="2025-08-10",
        crop_name="Maize",
        growth_stage="Pod Formation",
        latitude=lat,
        longitude=lon,
        weather=WeatherObservation(temperature=28.0, rainfall=20.0, humidity=75.0, wind_speed=11.5),
        satellite_features=SatelliteObservation(ndvi=0.82, ndmi=0.60, evi=0.70, vv=-9.8, vh=-15.5, cloud_percentage=10.0)
    )

    # Observation 5: Soybean - Maturity
    obs5 = builder.create_observation(
        date="2025-08-28",
        crop_name="Soybean",
        growth_stage="Maturity",
        latitude=lat,
        longitude=lon,
        weather=WeatherObservation(temperature=30.0, rainfall=5.0, humidity=60.0, wind_speed=9.0),
        satellite_features=SatelliteObservation(ndvi=0.35, ndmi=0.15, evi=0.25, vv=-13.0, vh=-20.0, cloud_percentage=2.0)
    )

    builder.add_observation(obs1)
    builder.add_observation(obs2)
    builder.add_observation(obs3)
    builder.add_observation(obs4)
    builder.add_observation(obs5)

    return builder.dataset
