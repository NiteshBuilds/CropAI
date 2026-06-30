from fastapi import APIRouter

from app.geofusion.schemas import UnifiedFeatureVector
from app.geofusion.feature_builder import FeatureBuilder

router = APIRouter(prefix="/geofusion", tags=["GeoFusion Engine"])


@router.get(
    "/template",
    response_model=UnifiedFeatureVector,
    summary="Get empty feature vector template",
    description="Returns an empty UnifiedFeatureVector structure with all data sources integrated."
)
async def get_geofusion_template() -> UnifiedFeatureVector:
    """Return an empty unified feature vector template."""
    builder = FeatureBuilder()
    return builder.build_empty_vector()


@router.get(
    "/sample",
    response_model=UnifiedFeatureVector,
    summary="Get sample feature vector",
    description="Returns a realistic sample UnifiedFeatureVector for the Sehore district context."
)
async def get_geofusion_sample() -> UnifiedFeatureVector:
    """Return a realistic sample unified feature vector."""
    builder = FeatureBuilder()
    return builder.build_sample_vector()
