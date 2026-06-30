"""
ai_decision_service.py
───────────────────────
Phase 13 — Unified AI Decision Engine.

Aggregates outputs from:
- Sentinel Processing Service
- Moisture Stress Service
- Irrigation Service
- Advisory Service
- Yield Prediction Service

Produces a single actionable AI decision for the farmer.
"""

import logging
from typing import Tuple

from app.schemas.advisory import AdvisoryRequest
from app.schemas.ai_decision import AIDecisionRequest, AIDecisionResponse
from app.schemas.irrigation import IrrigationRequest
from app.schemas.moisture_stress import MoistureStressRequest
from app.schemas.yield_prediction import YieldPredictionRequest
from app.services.advisory_service import advisory_service
from app.services.irrigation_service import irrigation_service
from app.services.moisture_stress_service import moisture_stress_service
from app.services.sentinel_processing_service import sentinel_processing_service
from app.services.yield_prediction_service import yield_prediction_service

logger = logging.getLogger(__name__)


class AIDecisionService:
    """
    Rule-based MVP engine for generating a unified AI decision.
    """

    async def analyze(self, request: AIDecisionRequest) -> AIDecisionResponse:
        """
        Runs all underlying AI engines and synthesises their outputs into
        a top-level farm status, priority, risk, and recommended action.
        """
        logger.info(
            "Unified AI Decision requested for %s (%s) at %.4f, %.4f on %s",
            request.crop,
            request.growth_stage,
            request.latitude,
            request.longitude,
            request.observation_date,
        )

        # 1. Sentinel Processing (used to satisfy dependency flow, though indices
        #    are also fetched internally by other services in this MVP architecture)
        await sentinel_processing_service.get_vegetation_indices(
            latitude=request.latitude,
            longitude=request.longitude,
            observation_date=request.observation_date,
        )

        # 2. Moisture Stress
        stress = await moisture_stress_service.analyze_stress(
            MoistureStressRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # 3. Irrigation Recommendation
        irrigation = await irrigation_service.recommend(
            IrrigationRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # 4. Advisory Service
        await advisory_service.generate(
            AdvisoryRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # 5. Yield Prediction
        yield_pred = await yield_prediction_service.predict(
            YieldPredictionRequest(
                crop=request.crop,
                growth_stage=request.growth_stage,
                latitude=request.latitude,
                longitude=request.longitude,
                observation_date=request.observation_date,
            )
        )

        # Apply Decision Rules
        farm_status, priority_level, risk_level, action, outcome = self._apply_rules(
            stress_level=stress.stress_level,
            irrigation_required=irrigation.irrigation_required,
            yield_category=yield_pred.yield_category,
        )

        # Confidence: average of Moisture Stress, Irrigation, and Yield Prediction
        avg_confidence = int(
            (stress.confidence + irrigation.confidence + yield_pred.confidence) / 3
        )
        # Clamp to 75-98 range
        confidence = max(75, min(98, avg_confidence))

        logger.info(
            "Unified AI Decision complete — status: %s | priority: %s",
            farm_status,
            priority_level,
        )

        return AIDecisionResponse(
            crop=request.crop,
            growth_stage=request.growth_stage,
            farm_status=farm_status,
            priority_level=priority_level,
            risk_level=risk_level,
            recommended_action=action,
            expected_outcome=outcome,
            confidence=confidence,
        )

    def _apply_rules(
        self, stress_level: str, irrigation_required: bool, yield_category: str
    ) -> Tuple[str, str, str, str, str]:
        """
        Priority-ordered rule evaluation.
        Returns: (farm_status, priority_level, risk_level, recommended_action, expected_outcome).
        """
        # CASE 3: Critical
        if stress_level == "High" and irrigation_required and yield_category == "Low":
            return (
                "Critical",
                "High",
                "High",
                "Immediate intervention required. Follow irrigation advisory and district recommendations.",
                "Potential yield loss if not addressed immediately.",
            )

        # CASE 1: Healthy (Checking healthy before moderate to ensure strict bounds)
        if stress_level == "Low" and not irrigation_required and yield_category == "High":
            return (
                "Healthy",
                "Low",
                "Low",
                "Continue routine monitoring.",
                "High yield expected if current conditions are maintained.",
            )

        # CASE 2: Monitor Closely (Moderate conditions)
        if stress_level == "Moderate" and irrigation_required and yield_category in ["Medium", "Average"]:
            return (
                "Monitor Closely",
                "Medium",
                "Moderate",
                "Apply recommended irrigation and monitor crop health.",
                "Yield can be maintained if intervention occurs within 24 hours.",
            )

        # Fallback 1: High stress but yield not categorised as 'Low' yet
        if stress_level == "High":
            return (
                "Critical",
                "High",
                "High",
                "Immediate intervention required. Follow irrigation advisory and district recommendations.",
                "Yield potential is at risk. Act immediately.",
            )

        # Fallback 2: Any irrigation required that isn't captured above
        if irrigation_required:
            return (
                "Monitor Closely",
                "Medium",
                "Moderate",
                "Apply recommended irrigation and monitor crop health.",
                "Yield can be maintained if intervention occurs within 24 hours.",
            )

        # Default Fallback: Generally stable
        return (
            "Healthy",
            "Low",
            "Low",
            "Continue routine monitoring.",
            "Crop is progressing normally.",
        )

    def build_sample_response(self) -> AIDecisionResponse:
        """Return a hardcoded demo decision payload."""
        return AIDecisionResponse(
            crop="Paddy",
            growth_stage="Vegetative",
            farm_status="Monitor Closely",
            priority_level="Medium",
            risk_level="Moderate",
            recommended_action="Apply recommended irrigation and monitor crop health.",
            expected_outcome="Yield can be maintained if intervention occurs within 24 hours.",
            confidence=94,
        )


ai_decision_service = AIDecisionService()
