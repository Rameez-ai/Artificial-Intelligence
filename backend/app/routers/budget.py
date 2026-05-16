"""
Smart Loan AI - Budget Router
"""

from fastapi import APIRouter, Depends
from models.schemas import BudgetInput, EMICalculation
from services.budget_service import BudgetService
from routers.auth import get_current_user

router = APIRouter()


@router.post("/analyze")
async def analyze_budget(budget: BudgetInput, current_user: dict = Depends(get_current_user)):
    """Analyze budget and get financial health score."""
    result = BudgetService.analyze_budget(budget.model_dump())
    return {"success": True, "data": result}


@router.post("/emi-calculator")
async def calculate_emi(emi: EMICalculation, current_user: dict = Depends(get_current_user)):
    """Calculate EMI and affordability."""
    monthly_income = 0
    result = BudgetService.calculate_emi(
        emi.loan_amount, emi.interest_rate, emi.loan_term, monthly_income
    )
    return {"success": True, "data": result}


@router.get("/health-score")
async def get_health_score(current_user: dict = Depends(get_current_user)):
    """Get quick financial health score based on latest data."""
    return {"success": True, "data": {"message": "Submit budget data via POST /analyze"}}
