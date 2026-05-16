"""
Smart Loan AI - Financial Router
==================================
Provides dashboard, health-score, risk-analysis, and simulation endpoints
that the Android app expects under /api/financial/...
"""

from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user
from services.budget_service import BudgetService
from services.loan_service import LoanService
from firebase.operations import FirebaseOperations
import datetime

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """
    GET /api/financial/dashboard
    Returns full dashboard data: stats, charts, insights, recent activity.
    """
    user_id = current_user["user_id"]

    # Fetch user's prediction history
    predictions = LoanService.get_history(user_id)

    # Latest prediction data
    latest = max(predictions, key=lambda x: x.get("created_at", ""), default=None) if predictions else None

    # Derive key metrics
    loan_probability = round(latest.get("probability", 0) * 100, 1) if latest else 0.0
    credit_score = latest.get("credit_score", 650) if latest else 650
    risk_level = latest.get("risk_level", "moderate") if latest else "moderate"

    # Compute financial health from latest prediction
    health_score = 70
    monthly_savings = 0.0
    dti_ratio = 0.0

    if latest:
        annual_income = latest.get("annual_income", 0)
        monthly_expenses = latest.get("monthly_expenses", 0)
        existing_debts = latest.get("existing_debts", 0)
        loan_amount = latest.get("loan_amount", 0)
        loan_term = latest.get("loan_term", 12)

        budget = BudgetService.analyze_budget({
            "annual_income": annual_income,
            "monthly_expenses": monthly_expenses,
            "existing_debts": existing_debts,
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "credit_score": credit_score
        })
        health_score = int(budget.get("health_score", 70))
        monthly_savings = budget["metrics"].get("monthly_savings", 0)
        dti_ratio = existing_debts / max(annual_income, 1)

    # Build income vs expenses chart data (last 5 months)
    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    income_vs_expenses = []
    for i, month in enumerate(months):
        base_income = (latest.get("annual_income", 60000) / 12) if latest else 5000
        base_expense = (latest.get("monthly_expenses", 3000)) if latest else 3000
        income_vs_expenses.append({
            "month": month,
            "income": round(base_income * (1 + 0.02 * i), 2),
            "expenses": round(base_expense * (1 - 0.01 * i), 2)
        })

    # Financial growth data
    financial_growth = []
    for i, month in enumerate(months):
        savings = monthly_savings * (i + 1) if monthly_savings > 0 else 500 * (i + 1)
        financial_growth.append({
            "month": month,
            "savings": round(savings, 2),
            "investments": round(savings * 0.3, 2),
            "net_worth": round(savings * 1.3, 2)
        })

    # Risk radar
    risk_radar = [
        {"category": "Credit", "value": min(credit_score / 8.5, 100)},
        {"category": "Income", "value": min(loan_probability + 20, 100)},
        {"category": "Debt", "value": max(100 - dti_ratio * 200, 0)},
        {"category": "Savings", "value": min(health_score, 100)},
        {"category": "Stability", "value": min(loan_probability + 10, 100)},
    ]

    # AI Insights
    insights = []
    if loan_probability >= 70:
        insights.append({
            "type": "success",
            "icon": "📈",
            "title": "Strong Approval Chance",
            "message": f"Your {loan_probability}% approval probability is excellent. Consider applying now."
        })
    elif loan_probability >= 50:
        insights.append({
            "type": "info",
            "icon": "💡",
            "title": "Good Standing",
            "message": f"You have a {loan_probability}% approval chance. Improving credit score can boost this."
        })
    else:
        insights.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Improve Before Applying",
            "message": f"Your current approval probability is {loan_probability}%. Focus on reducing debts."
        })

    if health_score >= 80:
        insights.append({
            "type": "success",
            "icon": "🏆",
            "title": "Financial Health Improved",
            "message": f"Your financial health score is {health_score}/100 — top 20% of applicants."
        })
    else:
        insights.append({
            "type": "info",
            "icon": "🎯",
            "title": "Health Score Tip",
            "message": f"Score {health_score}/100. Increasing savings rate by 5% can add 8 points."
        })

    # Recent activity
    recent_activity = []
    for pred in sorted(predictions, key=lambda x: x.get("created_at", ""), reverse=True)[:5]:
        recent_activity.append({
            "type": "prediction",
            "message": f"Loan check for ${pred.get('loan_amount', 0):,.0f}",
            "time": pred.get("created_at", "")[:10] if pred.get("created_at") else "Recently",
            "result": "Approved" if pred.get("approved") else "Rejected"
        })

    if not recent_activity:
        recent_activity.append({
            "type": "info",
            "message": "No loan checks yet. Run your first prediction!",
            "time": "Now",
            "result": "Pending"
        })

    return {
        "success": True,
        "data": {
            "loan_probability": loan_probability,
            "health_score": health_score,
            "risk_level": risk_level,
            "credit_score": credit_score,
            "monthly_savings": round(monthly_savings, 2),
            "dti_ratio": round(dti_ratio, 4),
            "insights": insights,
            "income_vs_expenses": income_vs_expenses,
            "financial_growth": financial_growth,
            "risk_radar": risk_radar,
            "emi_forecast": [],
            "recent_activity": recent_activity
        }
    }


@router.post("/health-score")
async def get_health_score(data: dict, current_user: dict = Depends(get_current_user)):
    """
    POST /api/financial/health-score
    Analyze budget and return financial health score.
    """
    try:
        result = BudgetService.analyze_budget(data)
        health_score = int(result.get("health_score", 0))
        grade = result.get("grade", "N/A")
        
        android_data = {
            "overall_score": health_score,
            "grade": grade,
            "grade_label": "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair",
            "summary": "Your financial health is stable but could use some improvements.",
            "breakdown": [
                {
                    "category": k.replace("_score", "").replace("_", " ").title(),
                    "score": int(v),
                    "reasoning": [f"Based on your {k.replace('_score', '').replace('_', ' ')}."]
                } for k, v in result.get("components", {}).items()
            ],
            "roadmap": [
                {
                    "category": "General",
                    "priority": r.get("type", "info").capitalize(),
                    "actions": [r.get("message", "")]
                } for r in result.get("recommendations", [])
            ]
        }
        return {"success": True, "data": android_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-analysis")
async def risk_analysis(data: dict, current_user: dict = Depends(get_current_user)):
    """
    POST /api/financial/risk-analysis
    Compute detailed risk analysis from financial inputs.
    """
    try:
        credit_score = data.get("credit_score", 650)
        annual_income = data.get("annual_income", 0)
        existing_debts = data.get("existing_debts", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        loan_amount = data.get("loan_amount", 0)
        loan_term = data.get("loan_term", 12)

        monthly_income = annual_income / 12
        dti = existing_debts / max(annual_income, 1)
        expense_ratio = monthly_expenses / max(monthly_income, 1)

        # Risk scoring
        credit_risk = "Low" if credit_score >= 720 else "Moderate" if credit_score >= 650 else "High"
        dti_risk = "Low" if dti < 0.2 else "Moderate" if dti < 0.4 else "High"
        expense_risk = "Low" if expense_ratio < 0.5 else "Moderate" if expense_ratio < 0.7 else "High"

        overall_risk_score = 0
        if credit_score >= 750: overall_risk_score += 30
        elif credit_score >= 700: overall_risk_score += 22
        elif credit_score >= 650: overall_risk_score += 14
        if dti < 0.2: overall_risk_score += 25
        elif dti < 0.35: overall_risk_score += 18
        elif dti < 0.5: overall_risk_score += 10
        if expense_ratio < 0.5: overall_risk_score += 25
        elif expense_ratio < 0.7: overall_risk_score += 15
        if annual_income >= 80000: overall_risk_score += 20
        elif annual_income >= 50000: overall_risk_score += 14
        elif annual_income >= 30000: overall_risk_score += 8

        overall_level = "Low Risk" if overall_risk_score >= 70 else "Moderate Risk" if overall_risk_score >= 45 else "High Risk"

        android_data = {
            "risk_level": overall_level,
            "overall_risk": overall_risk_score,
            "risk_color": "#F44336" if "High" in overall_level else "#FFC107" if "Moderate" in overall_level else "#4CAF50",
            "summary": f"Your profile is assessed as {overall_level}.",
            "dimensions": [
                {
                    "dimension": "Credit History",
                    "severity": credit_risk,
                    "value": str(credit_score),
                    "score": int(credit_score / 8.5),
                    "message": f"Credit score is {credit_score}"
                },
                {
                    "dimension": "Debt-to-Income",
                    "severity": dti_risk,
                    "value": f"{round(dti*100, 1)}%",
                    "score": int(max(0, 100 - dti*100)),
                    "message": f"DTI is {round(dti*100, 1)}%"
                },
                {
                    "dimension": "Expense Ratio",
                    "severity": expense_risk,
                    "value": f"{round(expense_ratio*100, 1)}%",
                    "score": int(max(0, 100 - expense_ratio*100)),
                    "message": f"Expense ratio is {round(expense_ratio*100, 1)}%"
                }
            ]
        }

        return {
            "success": True,
            "data": android_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate")
async def simulate_loan(data: dict, current_user: dict = Depends(get_current_user)):
    """
    POST /api/financial/simulate
    Simulate EMI scenarios for different loan amounts and terms.
    """
    try:
        loan_amount = data.get("loan_amount", 10000)
        interest_rate = data.get("interest_rate", 8.5)
        loan_term = data.get("loan_term", 12)
        annual_income = data.get("annual_income", 60000)

        monthly_income = annual_income / 12
        result = BudgetService.calculate_emi(loan_amount, interest_rate, loan_term, monthly_income)

        # Scenario variations
        scenarios = []
        for term_mult in [0.5, 1.0, 1.5, 2.0]:
            t = max(int(loan_term * term_mult), 6)
            s = BudgetService.calculate_emi(loan_amount, interest_rate, t, monthly_income)
            scenarios.append({
                "term_months": t,
                "monthly_emi": s["monthly_emi"],
                "total_interest": s["total_interest"],
                "affordable": s["affordable"]
            })

        # EMI forecast (monthly breakdown for chart)
        emi_forecast = []
        import math
        monthly_rate = interest_rate / 100 / 12
        balance = loan_amount
        for month in range(1, min(loan_term + 1, 13)):
            interest_payment = balance * monthly_rate if monthly_rate > 0 else 0
            principal_payment = result["monthly_emi"] - interest_payment
            balance = max(balance - principal_payment, 0)
            emi_forecast.append({
                "month": f"M{month}",
                "emi": result["monthly_emi"],
                "remaining": round(balance, 2)
            })

        baseline_savings = data.get("savings_balance", 0)
        monthly_savings = monthly_income - data.get("monthly_expenses", 0)
        
        baseline_trajectory = []
        projected_trajectory = []
        chart_data = []

        b_savings = baseline_savings
        p_savings = baseline_savings
        
        for m in range(1, 13):
            b_savings += monthly_savings
            p_savings += (monthly_savings - result["monthly_emi"])
            
            baseline_trajectory.append({
                "month": m,
                "savings": round(b_savings, 2),
                "net_income": monthly_income,
                "cumulative_interest": 0
            })
            projected_trajectory.append({
                "month": m,
                "savings": round(max(p_savings, 0), 2),
                "net_income": monthly_income,
                "cumulative_interest": round((result["monthly_emi"] * m) - loan_amount * (m / loan_term), 2)
            })
            chart_data.append({
                "month": f"M{m}",
                "baseline": round(b_savings, 2),
                "projected": round(max(p_savings, 0), 2)
            })

        android_data = {
            "summary": "Simulation based on your requested loan.",
            "baseline": {
                "trajectory": baseline_trajectory,
                "final_savings": round(baseline_trajectory[-1]["savings"], 2) if baseline_trajectory else 0,
                "monthly_net": monthly_savings,
                "current_emi": 0.0,
                "new_emi": 0.0
            },
            "projected": {
                "trajectory": projected_trajectory,
                "final_savings": round(projected_trajectory[-1]["savings"], 2) if projected_trajectory else 0,
                "monthly_net": monthly_savings - result["monthly_emi"],
                "current_emi": 0.0,
                "new_emi": result["monthly_emi"]
            },
            "comparison": {
                "savings_difference": round(b_savings - p_savings, 2),
                "monthly_difference": result["monthly_emi"],
                "emi_difference": result["monthly_emi"],
                "projection_months": 12
            },
            "chart_data": chart_data,
            "recommendations": [
                {"type": "info", "message": f"Your new EMI will be ${result['monthly_emi']}/month."}
            ]
        }

        return {
            "success": True,
            "data": android_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
