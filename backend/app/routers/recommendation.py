"""
Smart Loan AI - Recommendation Router
"""

from fastapi import APIRouter, Depends
from models.schemas import RecommendationFeedback
from services.rl_service import RLService
from routers.auth import get_current_user

router = APIRouter()


@router.post("/get")
async def get_recommendations(profile: dict, current_user: dict = Depends(get_current_user)):
    """Get personalized RL-based recommendations."""
    result = RLService.get_recommendations(profile, current_user["user_id"])
    return {"success": True, "data": result}


@router.post("/feedback")
async def submit_feedback(feedback: RecommendationFeedback, current_user: dict = Depends(get_current_user)):
    """Submit feedback on a recommendation."""
    result = RLService.submit_feedback(
        current_user["user_id"], feedback.recommendation_id,
        feedback.helpful, feedback.action_taken
    )
    return {"success": True, "data": result}
