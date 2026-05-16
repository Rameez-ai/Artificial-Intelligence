"""
Smart Loan AI - Budget Analysis Service
=========================================
Budget analysis, EMI calculation, and financial health scoring.
"""

import math
from ml.feature_engineering import compute_financial_health_score


class BudgetService:
    """Budget analysis and EMI calculation service."""

    @staticmethod
    def analyze_budget(data: dict) -> dict:
        """Comprehensive budget analysis."""
        annual_income = data.get('annual_income', 0)
        monthly_expenses = data.get('monthly_expenses', 0)
        existing_debts = data.get('existing_debts', 0)
        loan_amount = data.get('loan_amount', 0)
        loan_term = data.get('loan_term', 12)
        credit_score = data.get('credit_score', 650)

        monthly_income = annual_income / 12
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = monthly_savings / max(monthly_income, 1) * 100

        # Financial health
        health = compute_financial_health_score(
            annual_income, monthly_expenses, existing_debts,
            credit_score, loan_amount, loan_term
        )

        # Expense breakdown
        expense_breakdown = data.get('expense_breakdown', {})
        if not expense_breakdown:
            expense_breakdown = {
                'Housing': monthly_expenses * 0.35,
                'Food': monthly_expenses * 0.20,
                'Transportation': monthly_expenses * 0.15,
                'Utilities': monthly_expenses * 0.10,
                'Entertainment': monthly_expenses * 0.10,
                'Other': monthly_expenses * 0.10
            }

        # Recommendations
        recommendations = []
        if savings_rate < 10:
            recommendations.append({
                'type': 'warning',
                'message': f'Your savings rate ({savings_rate:.1f}%) is very low. Aim for at least 20%.'
            })
        elif savings_rate < 20:
            recommendations.append({
                'type': 'info',
                'message': f'Your savings rate ({savings_rate:.1f}%) could be improved. Target 20-30%.'
            })
        else:
            recommendations.append({
                'type': 'success',
                'message': f'Great savings rate of {savings_rate:.1f}%! Keep it up.'
            })

        dti = existing_debts / max(annual_income, 1)
        if dti > 0.4:
            recommendations.append({
                'type': 'warning',
                'message': f'Your debt-to-income ratio ({dti:.0%}) is high. Focus on debt reduction.'
            })

        if monthly_savings < monthly_income * 0.1:
            recommendations.append({
                'type': 'info',
                'message': 'Consider building a 3-6 month emergency fund.'
            })

        return {
            'health_score': health['health_score'],
            'grade': health['grade'],
            'components': health['components'],
            'metrics': {
                **health['metrics'],
                'monthly_income': round(monthly_income, 2),
                'monthly_savings': round(monthly_savings, 2),
                'savings_rate': round(savings_rate, 1),
                'annual_income': annual_income,
            },
            'expense_breakdown': {k: round(v, 2) for k, v in expense_breakdown.items()},
            'recommendations': recommendations
        }

    @staticmethod
    def calculate_emi(loan_amount: float, interest_rate: float, loan_term: int,
                      monthly_income: float = 0) -> dict:
        """Calculate EMI and affordability."""
        monthly_rate = interest_rate / 100 / 12

        if monthly_rate > 0:
            emi = loan_amount * monthly_rate * math.pow(1 + monthly_rate, loan_term) / \
                  (math.pow(1 + monthly_rate, loan_term) - 1)
        else:
            emi = loan_amount / loan_term

        total_payment = emi * loan_term
        total_interest = total_payment - loan_amount

        emi_to_income = emi / max(monthly_income, 1) if monthly_income > 0 else 0
        affordable = emi_to_income <= 0.3

        return {
            'monthly_emi': round(emi, 2),
            'total_payment': round(total_payment, 2),
            'total_interest': round(total_interest, 2),
            'affordable': affordable,
            'emi_to_income_ratio': round(emi_to_income * 100, 1),
            'amortization_summary': {
                'first_month_interest': round(loan_amount * monthly_rate, 2) if monthly_rate > 0 else 0,
                'first_month_principal': round(emi - loan_amount * monthly_rate, 2) if monthly_rate > 0 else round(emi, 2),
            }
        }
