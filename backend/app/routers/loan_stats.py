"""
Smart Loan AI - Loans Router (Plural)
=======================================
Plural-path aliases + stats endpoint that the Android app expects
under /api/loan/... (existing) and adds /api/loan/stats.
This router is mounted at /api/loan (same prefix as existing loan.py
but adds the missing /stats endpoint cleanly via the existing router).
"""

from fastapi import APIRouter, HTTPException, Depends
from services.loan_service import LoanService
from routers.auth import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_loan_stats(current_user: dict = Depends(get_current_user)):
    """
    GET /api/loan/stats
    Returns aggregated loan statistics for the current user.
    """
    try:
        history = LoanService.get_history(current_user["user_id"])

        total = len(history)
        approved = sum(1 for p in history if p.get("approved"))
        rejected = total - approved
        avg_probability = (
            round(sum(p.get("probability", 0) for p in history) / total * 100, 1)
            if total > 0 else 0.0
        )
        avg_credit_score = (
            round(sum(p.get("credit_score", 0) for p in history) / total)
            if total > 0 else 0
        )
        latest = max(history, key=lambda x: x.get("created_at", ""), default=None) if history else None

        return {
            "success": True,
            "data": {
                "total_predictions": total,
                "approved": approved,
                "rejected": rejected,
                "approval_rate": round(approved / max(total, 1) * 100, 1),
                "avg_probability": avg_probability,
                "avg_credit_score": avg_credit_score,
                "last_prediction_date": latest.get("created_at", "") if latest else None,
                "last_result": "Approved" if latest and latest.get("approved") else "Rejected" if latest else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
