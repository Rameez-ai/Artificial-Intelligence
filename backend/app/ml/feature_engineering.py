"""
Smart Loan AI - Feature Engineering Module
==========================================
Provides feature engineering utilities for loan prediction.
Used both during training and real-time prediction.
"""

import numpy as np
import pandas as pd


def compute_risk_category(credit_score: float) -> str:
    """
    Assign a risk category based on credit score.

    Args:
        credit_score: The applicant's credit score (300-850)

    Returns:
        Risk category string
    """
    if credit_score >= 750:
        return 'Very Low Risk'
    elif credit_score >= 700:
        return 'Low Risk'
    elif credit_score >= 650:
        return 'Moderate Risk'
    elif credit_score >= 600:
        return 'High Risk'
    else:
        return 'Very High Risk'


def compute_financial_health_score(
    annual_income: float,
    monthly_expenses: float,
    existing_debts: float,
    credit_score: float,
    loan_amount: float = 0,
    loan_term: int = 12
) -> dict:
    """
    Compute a comprehensive financial health score (0-100).

    Args:
        annual_income: Annual income in dollars
        monthly_expenses: Monthly expenses
        existing_debts: Total existing debts
        credit_score: Credit score (300-850)
        loan_amount: Requested loan amount
        loan_term: Loan term in months

    Returns:
        Dict with health_score, component scores, and recommendations
    """
    monthly_income = annual_income / 12

    # Component 1: Savings Rate Score (0-25)
    savings_rate = (monthly_income - monthly_expenses) / max(monthly_income, 1)
    savings_score = min(25, max(0, savings_rate * 50))

    # Component 2: Debt-to-Income Score (0-25)
    dti = existing_debts / max(annual_income, 1)
    dti_score = max(0, 25 - (dti * 50))

    # Component 3: Credit Score Component (0-25)
    credit_component = ((credit_score - 300) / 550) * 25

    # Component 4: EMI Affordability (0-25)
    if loan_amount > 0 and loan_term > 0:
        # Simple EMI calculation (without interest for simplicity)
        monthly_emi = loan_amount / loan_term
        emi_ratio = monthly_emi / max(monthly_income - monthly_expenses, 1)
        emi_score = max(0, 25 - (emi_ratio * 25))
    else:
        emi_score = 25  # No loan, full score

    total_score = round(savings_score + dti_score + credit_component + emi_score, 1)
    total_score = min(100, max(0, total_score))

    return {
        'health_score': total_score,
        'grade': _score_to_grade(total_score),
        'components': {
            'savings_rate_score': round(savings_score, 1),
            'debt_management_score': round(dti_score, 1),
            'credit_health_score': round(credit_component, 1),
            'emi_affordability_score': round(emi_score, 1)
        },
        'metrics': {
            'savings_rate': round(savings_rate * 100, 1),
            'debt_to_income_ratio': round(dti * 100, 1),
            'monthly_disposable': round(monthly_income - monthly_expenses, 2)
        }
    }


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 85:
        return 'A+'
    elif score >= 75:
        return 'A'
    elif score >= 65:
        return 'B'
    elif score >= 50:
        return 'C'
    elif score >= 35:
        return 'D'
    else:
        return 'F'


def generate_improvement_suggestions(
    credit_score: float,
    annual_income: float,
    monthly_expenses: float,
    existing_debts: float,
    loan_amount: float,
    loan_term: int,
    employment_status: str,
    education: str
) -> list:
    """
    Generate personalized suggestions for improving loan eligibility.

    Args:
        All loan application fields

    Returns:
        List of suggestion strings with priority levels
    """
    suggestions = []
    monthly_income = annual_income / 12
    dti = existing_debts / max(annual_income, 1)
    savings_rate = (monthly_income - monthly_expenses) / max(monthly_income, 1)
    loan_to_income = loan_amount / max(annual_income, 1)

    # Credit score suggestions
    if credit_score < 600:
        suggestions.append({
            'priority': 'high',
            'category': 'Credit Score',
            'suggestion': 'Your credit score is below 600. Focus on paying bills on time and reducing credit utilization to improve it.',
            'impact': 'Could increase approval probability by 30-40%'
        })
    elif credit_score < 700:
        suggestions.append({
            'priority': 'medium',
            'category': 'Credit Score',
            'suggestion': 'Improving your credit score above 700 would significantly boost approval chances.',
            'impact': 'Could increase approval probability by 15-25%'
        })

    # DTI suggestions
    if dti > 0.4:
        suggestions.append({
            'priority': 'high',
            'category': 'Debt Management',
            'suggestion': f'Your debt-to-income ratio is {dti:.0%}, which is very high. Try to pay down existing debts before applying.',
            'impact': 'Reducing DTI below 35% could increase approval chances by 20-30%'
        })
    elif dti > 0.25:
        suggestions.append({
            'priority': 'medium',
            'category': 'Debt Management',
            'suggestion': f'Consider reducing your debt-to-income ratio from {dti:.0%} to below 25%.',
            'impact': 'Could improve your financial profile significantly'
        })

    # Savings rate suggestions
    if savings_rate < 0.1:
        suggestions.append({
            'priority': 'high',
            'category': 'Savings',
            'suggestion': 'Your savings rate is very low. Reducing monthly expenses could demonstrate better financial stability.',
            'impact': 'A savings rate above 20% shows lenders you can handle loan payments'
        })

    # Loan amount suggestions
    if loan_to_income > 3:
        suggestions.append({
            'priority': 'high',
            'category': 'Loan Amount',
            'suggestion': f'The requested loan amount is {loan_to_income:.1f}x your annual income. Consider requesting a smaller amount.',
            'impact': 'A loan-to-income ratio below 3x is generally more favorable'
        })
    elif loan_to_income > 2:
        suggestions.append({
            'priority': 'medium',
            'category': 'Loan Amount',
            'suggestion': 'Consider reducing the loan amount or extending the term to improve affordability.',
            'impact': 'Lower monthly payments improve EMI-to-income ratio'
        })

    # Employment suggestions
    if employment_status in ['Unemployed', 'Part-Time']:
        suggestions.append({
            'priority': 'high',
            'category': 'Employment',
            'suggestion': 'Full-time employment significantly improves loan approval chances.',
            'impact': 'Employed applicants have 2-3x higher approval rates'
        })

    # Loan term suggestion
    emi = loan_amount / max(loan_term, 1)
    if emi > monthly_income * 0.4:
        suggestions.append({
            'priority': 'medium',
            'category': 'Loan Term',
            'suggestion': 'Consider extending your loan term to reduce monthly EMI burden.',
            'impact': 'EMI should ideally be below 30% of monthly income'
        })

    # General positive suggestions
    if not suggestions:
        suggestions.append({
            'priority': 'low',
            'category': 'General',
            'suggestion': 'Your financial profile looks strong! Maintain your current financial habits.',
            'impact': 'You have a good chance of loan approval'
        })

    return suggestions


def prepare_single_prediction(data: dict) -> pd.DataFrame:
    """
    Prepare a single user input for prediction.

    Args:
        data: Dict with user input fields

    Returns:
        DataFrame ready for preprocessor.transform()
    """
    df = pd.DataFrame([data])

    monthly_income = df['annual_income'] / 12
    estimated_emi = df['loan_amount'] / df['loan_term'].replace(0, 1)

    df['debt_to_income_ratio'] = (
        df['existing_debts'] / df['annual_income'].replace(0, 1)
    ).round(4)

    df['loan_to_income_ratio'] = (
        df['loan_amount'] / df['annual_income'].replace(0, 1)
    ).round(4)

    df['monthly_debt_burden'] = (
        (df['existing_debts'] / 12 + estimated_emi) / monthly_income.replace(0, 1)
    ).round(4)

    df['savings_rate'] = (
        (monthly_income - df['monthly_expenses']) / monthly_income.replace(0, 1)
    ).round(4)

    df['emi_to_income_ratio'] = (
        estimated_emi / monthly_income.replace(0, 1)
    ).round(4)

    return df
