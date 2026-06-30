"""
ai_decision.py  (api router)
─────────────────────────────
Router prefix : /api/ai-decision
Tag           : AI Decision

Endpoints
---------
GET  /api/ai-decision/sample   — demo payload, no inputs required
POST /api/ai-decision/analyze  — top-level AI decision aggregating all engines
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.ai_decision import AIDecisionRequest, AIDecisionResponse
from app.services.ai_decision_service import ai_decision_service

router = APIRouter(prefix="/ai-decision", tags=["AI Decision"])


@router.get(
    "/sample",
    response_model=AIDecisionResponse,
    summary="Get sample AI decision",
    description="Returns a realistic hardcoded AI decision payload for demonstration.",
)
async def get_ai_decision_sample() -> AIDecisionResponse:
    """Return a pre-built sample AI decision payload."""
    return ai_decision_service.build_sample_response()


@router.post(
    "/analyze",
    response_model=AIDecisionResponse,
    summary="Generate unified AI decision",
    description=(
        "Executes the full pipeline of underlying AI engines and synthesises "
        "their outputs into a final actionable decision for the farmer."
    ),
)
async def analyze_ai_decision(request: AIDecisionRequest) -> AIDecisionResponse:
    """Run the unified decision engine for the given field parameters."""
    try:
        return await ai_decision_service.analyze(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unified AI Decision engine failed: {exc}",
        ) from exc
