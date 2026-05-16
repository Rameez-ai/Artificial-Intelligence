"""
Smart Loan AI - Reports Router
================================
Provides report generation and history endpoints that the Android app
expects under /api/reports/...
"""

from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user
from services.loan_service import LoanService
from services.budget_service import BudgetService
from firebase.operations import FirebaseOperations
import datetime

router = APIRouter()

REPORTS_COLLECTION = "reports"


@router.post("/generate")
async def generate_report(data: dict, current_user: dict = Depends(get_current_user)):
    """
    POST /api/reports/generate
    Generate a financial report for the current user.
    Accepted body: { "type": "loan" | "budget" | "full" }
    """
    try:
        user_id = current_user["user_id"]
        report_type = data.get("type", "full")

        # Fetch user history
        predictions = LoanService.get_history(user_id)
        total = len(predictions)
        approved = sum(1 for p in predictions if p.get("approved"))
        latest = (
            max(predictions, key=lambda x: x.get("created_at", ""), default=None)
            if predictions else None
        )

        # Build report content
        summary = {
            "total_predictions": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": round(approved / max(total, 1) * 100, 1),
        }

        financial_health = None
        if latest:
            budget = BudgetService.analyze_budget({
                "annual_income": latest.get("annual_income", 0),
                "monthly_expenses": latest.get("monthly_expenses", 0),
                "existing_debts": latest.get("existing_debts", 0),
                "credit_score": latest.get("credit_score", 650),
                "loan_amount": latest.get("loan_amount", 0),
                "loan_term": latest.get("loan_term", 12),
            })
            financial_health = {
                "health_score": budget.get("health_score"),
                "grade": budget.get("grade"),
                "recommendations": budget.get("recommendations", [])
            }

        title_map = {
            "financial_summary": "Financial Summary",
            "loan_analysis": "Loan Analysis",
            "risk_report": "Risk Report",
            "ai_recommendations": "AI Recommendations"
        }
        report_title = title_map.get(report_type, f"{report_type.capitalize()} Report")

        sections = []
        sections.append({
            "title": "Account Summary",
            "content": f"Total Predictions: {total}",
            "items": [
                {"label": "Approved Loans", "value": str(approved), "status": "Success"},
                {"label": "Rejected Loans", "value": str(total - approved), "status": "Warning"},
                {"label": "Approval Rate", "value": f"{round(approved / max(total, 1) * 100, 1)}%", "status": "Info"}
            ]
        })

        if financial_health:
            sections.append({
                "title": "Financial Health",
                "content": f"Your current financial grade is {financial_health.get('grade', 'N/A')}.",
                "items": [
                    {"label": "Health Score", "value": str(financial_health.get('health_score', 0)), "status": "Info"}
                ]
            })
            
            recommendations = financial_health.get("recommendations", [])
            if recommendations:
                sections.append({
                    "title": "AI Recommendations",
                    "content": "Suggested steps to improve your financial standing.",
                    "items": [
                        {"label": "Suggestion", "value": r.get("message", ""), "status": "Info"}
                        for r in recommendations
                    ]
                })

        report = {
            "id": f"RPT-{user_id[:6].upper()}-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "user_id": user_id,
            "type": report_type,
            "title": report_title,
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "sections": sections
        }

        # Save to Firebase
        report_id = FirebaseOperations.create(REPORTS_COLLECTION, report)
        report["id"] = report_id

        return {"success": True, "data": report}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_report_history(current_user: dict = Depends(get_current_user)):
    """
    GET /api/reports/history
    Returns list of previously generated reports for the user.
    """
    try:
        reports = FirebaseOperations.query(
            REPORTS_COLLECTION, "user_id", "==", current_user["user_id"]
        )
        history = [
            {
                "id": r.get("id", r.get("report_id", "")),
                "type": r.get("type", "full"),
                "title": r.get("title", "Financial Report"),
                "date": r.get("generated_at", "")[:10] if r.get("generated_at") else "N/A"
            }
            for r in sorted(reports, key=lambda x: x.get("generated_at", ""), reverse=True)
        ]
        return {"success": True, "data": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
