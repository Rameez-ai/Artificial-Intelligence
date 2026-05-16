import json
from services.budget_service import BudgetService

data = {
    'monthly_income': 5000,
    'monthly_expenses': 2000,
    'credit_score': 700,
    'loan_amount': 10000,
    'loan_term': 12
}

result = BudgetService.analyze_budget(data)
health_score = result.get('health_score', 0)
grade = result.get('grade', 'N/A')

android_data = {
    "overall_score": health_score,
    "grade": grade,
    "grade_label": "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair",
    "summary": "Your financial health is stable but could use some improvements.",
    "breakdown": [
        {
            "category": k.replace("_score", "").replace("_", " ").title(),
            "score": int(v),
            "reasoning": [f"Based on your profile."]
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

print(json.dumps(android_data, indent=2))
