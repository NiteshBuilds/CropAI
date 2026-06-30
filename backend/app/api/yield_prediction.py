"""
yield_prediction.py  (api router)
───────────────────────────────────
Router prefix : /api/yield
Tag           : Yield Prediction

Endpoints
---------
GET  /api/yield/sample   — hardcoded demo payload, no inputs required
POST /api/yield/predict  — live prediction from field parameters
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.yield_prediction import YieldPredictionRequest, YieldPredictionResponse
from app.services.yield_prediction_service import yield_prediction_service

router = APIRouter(prefix="/yield", tags=["Yield Prediction"])


@router.get(
    "/sample",
    response_model=YieldPredictionResponse,
    summary="Get sample yield prediction",
    description=(
        "Returns a realistic hardcoded yield prediction for demonstration "
        "and Swagger documentation purposes. No inputs required."
    ),
)
async def get_yield_sample() -> YieldPredictionResponse:
    """Return a pre-built sample yield prediction."""
    return yield_prediction_service.build_sample_response()


@router.post(
    "/predict",
    response_model=YieldPredictionResponse,
    summary="Predict crop yield",
    description=(
        "Accepts field parameters, internally calls Sentinel-2 Processing, "
        "Moisture Stress, and Weather services, then returns a structured "
        "yield prediction."
    ),
)
async def predict_yield(request: YieldPredictionRequest) -> YieldPredictionResponse:
    """Run the yield prediction engine for the given field observation."""
    try:
        return await yield_prediction_service.predict(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Yield prediction engine failed: {exc}",
        ) from exc
