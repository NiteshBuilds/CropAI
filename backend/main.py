import app.core.config  # noqa: F401 – loads .env before settings are evaluated

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.services_health import router as services_health_router
from app.api.copernicus import router as copernicus_router
from app.api.config import router as config_router
from app.api.dataset import router as dataset_router
from app.satellite.router import router as satellite_router
from app.geofusion.router import router as geofusion_router
from app.api.sentinel_processing import router as sentinel_processing_router
from app.api.moisture_stress import router as moisture_stress_router
from app.api.irrigation import router as irrigation_router
from app.api.advisory import router as advisory_router
from app.api.dashboard import router as dashboard_router
from app.api.yield_prediction import router as yield_prediction_router
from app.api.ai_decision import router as ai_decision_router
from app.core.settings import settings

application = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-Driven Automated Crop Type, Moisture Stress Detection "
        "and Irrigation Advisory Across Growth Stages Using Multi-source Satellite Data"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.include_router(health_router)
application.include_router(services_health_router, prefix="/api")
application.include_router(copernicus_router, prefix="/api")
application.include_router(config_router, prefix="/api")
application.include_router(dataset_router, prefix="/api")
application.include_router(satellite_router, prefix="/api")
application.include_router(geofusion_router, prefix="/api")
application.include_router(sentinel_processing_router, prefix="/api")
application.include_router(moisture_stress_router, prefix="/api")
application.include_router(irrigation_router, prefix="/api")
application.include_router(advisory_router, prefix="/api")
application.include_router(dashboard_router, prefix="/api")
application.include_router(yield_prediction_router, prefix="/api")
application.include_router(ai_decision_router, prefix="/api")
app = application
