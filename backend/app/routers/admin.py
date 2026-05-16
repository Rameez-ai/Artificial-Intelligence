"""
Smart Loan AI - Admin Router
"""

from fastapi import APIRouter, HTTPException, Depends
from services.auth_service import AuthService
from services.loan_service import LoanService
from services.chatbot_service import ChatbotService
from services.rl_service import RLService
from services.eda_service import EDAService
from routers.auth import get_current_user
from firebase.operations import FirebaseOperations
import json, os

router = APIRouter()


def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency: require admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    """List all registered users."""
    users = AuthService.get_all_users()
    return {"success": True, "data": users, "total": len(users)}


@router.get("/analytics")
async def prediction_analytics(admin: dict = Depends(require_admin)):
    """Get prediction analytics."""
    predictions = LoanService.get_all_predictions()
    total = len(predictions)
    approved = sum(1 for p in predictions if p.get('approved'))
    return {
        "success": True,
        "data": {
            "total_predictions": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": round(approved / max(total, 1) * 100, 1)
        }
    }


@router.get("/chatbot-logs")
async def chatbot_logs(admin: dict = Depends(require_admin)):
    """Get chatbot conversation logs."""
    logs = ChatbotService.get_all_logs()
    return {"success": True, "data": logs, "total": len(logs)}


@router.get("/model-stats")
async def model_stats(admin: dict = Depends(require_admin)):
    """Get ML model statistics."""
    stats_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model_comparison.json')
    if os.path.exists(stats_path):
        with open(stats_path, 'r') as f:
            return {"success": True, "data": json.load(f)}
    return {"success": True, "data": {"message": "Model not trained yet"}}


@router.get("/eda-reports")
async def eda_reports(admin: dict = Depends(require_admin)):
    """Get EDA reports."""
    reports = EDAService.get_reports()
    return {"success": True, "data": reports}


@router.get("/rl-metrics")
async def rl_metrics(admin: dict = Depends(require_admin)):
    """Get RL agent performance metrics."""
    metrics = RLService.get_metrics()
    return {"success": True, "data": metrics}


@router.get("/dashboard")
async def admin_dashboard(admin: dict = Depends(require_admin)):
    """Get complete admin dashboard data."""
    users = AuthService.get_all_users()
    predictions = LoanService.get_all_predictions()
    approved = sum(1 for p in predictions if p.get('approved'))
    total_chats = len(ChatbotService.get_all_logs())

    return {
        "success": True,
        "data": {
            "total_users": len(users),
            "total_predictions": len(predictions),
            "approved": approved,
            "rejected": len(predictions) - approved,
            "approval_rate": round(approved / max(len(predictions), 1) * 100, 1),
            "total_chats": total_chats,
            "rl_metrics": RLService.get_metrics()
        }
    }
