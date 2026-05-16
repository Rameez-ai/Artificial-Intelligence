"""
Smart Loan AI - Synthetic Loan Dataset Generator
=================================================
Generates a realistic synthetic loan dataset with correlated features
for training the loan eligibility prediction model.

Usage:
    python generate_sample_data.py [--rows 5000] [--output ../data/raw/loan_dataset.csv]
"""

import numpy as np
import pandas as pd
import argparse
import os
from datetime import datetime


def generate_loan_dataset(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic loan dataset with realistic distributions and correlations.

    Parameters:
        n_rows: Number of rows to generate
        seed: Random seed for reproducibility

    Returns:
        pd.DataFrame with loan application data
    """
    np.random.seed(seed)

    # --- Age: Normal distribution, 21-65 ---
    age = np.clip(np.random.normal(loc=35, scale=10, size=n_rows), 21, 65).astype(int)

    # --- Gender ---
    gender = np.random.choice(['Male', 'Female', 'Other'], size=n_rows, p=[0.55, 0.42, 0.03])

    # --- Education ---
    education = np.random.choice(
        ['High School', 'Associate', 'Bachelor', 'Master', 'PhD'],
        size=n_rows,
        p=[0.20, 0.15, 0.35, 0.22, 0.08]
    )

    # --- Employment Status ---
    employment_status = np.random.choice(
        ['Employed', 'Self-Employed', 'Unemployed', 'Part-Time', 'Retired'],
        size=n_rows,
        p=[0.50, 0.20, 0.10, 0.12, 0.08]
    )

    # --- Annual Income: Correlated with education and employment ---
    education_income_multiplier = {
        'High School': 0.7, 'Associate': 0.85, 'Bachelor': 1.0,
        'Master': 1.3, 'PhD': 1.5
    }
    employment_income_multiplier = {
        'Employed': 1.0, 'Self-Employed': 1.1, 'Unemployed': 0.2,
        'Part-Time': 0.5, 'Retired': 0.6
    }

    base_income = np.random.lognormal(mean=10.8, sigma=0.5, size=n_rows)
    annual_income = np.array([
        base_income[i] * education_income_multiplier[education[i]] *
        employment_income_multiplier[employment_status[i]]
        for i in range(n_rows)
    ])
    annual_income = np.clip(annual_income, 5000, 500000).astype(int)

    # --- Monthly Expenses: 30-80% of monthly income ---
    monthly_income = annual_income / 12
    expense_ratio = np.random.uniform(0.30, 0.80, size=n_rows)
    monthly_expenses = (monthly_income * expense_ratio).astype(int)

    # --- Existing Debts: Correlated with income ---
    debt_ratio = np.random.exponential(scale=0.15, size=n_rows)
    debt_ratio = np.clip(debt_ratio, 0, 0.8)
    existing_debts = (annual_income * debt_ratio).astype(int)

    # --- Loan Amount: Between 5K and 500K ---
    loan_amount = np.random.lognormal(mean=10.2, sigma=0.8, size=n_rows)
    loan_amount = np.clip(loan_amount, 5000, 500000).astype(int)

    # --- Loan Term (months): 12, 24, 36, 48, 60, 84, 120, 180, 240, 360 ---
    loan_term = np.random.choice(
        [12, 24, 36, 48, 60, 84, 120, 180, 240, 360],
        size=n_rows,
        p=[0.05, 0.08, 0.12, 0.10, 0.15, 0.12, 0.15, 0.10, 0.08, 0.05]
    )

    # --- Credit Score: 300-850, normally distributed ---
    credit_score = np.clip(
        np.random.normal(loc=650, scale=100, size=n_rows), 300, 850
    ).astype(int)

    # --- Derive Loan Approval (target variable) ---
    # Approval depends on multiple weighted factors
    approval_score = np.zeros(n_rows)

    # Credit score contribution (0-35 points)
    approval_score += np.where(credit_score >= 750, 35,
                      np.where(credit_score >= 700, 28,
                      np.where(credit_score >= 650, 20,
                      np.where(credit_score >= 600, 12,
                      np.where(credit_score >= 500, 5, 0)))))

    # Debt-to-income ratio contribution (0-25 points)
    dti = (existing_debts + (loan_amount / (loan_term / 12))) / annual_income
    approval_score += np.where(dti < 0.2, 25,
                      np.where(dti < 0.35, 20,
                      np.where(dti < 0.45, 12,
                      np.where(dti < 0.55, 5, 0))))

    # Employment contribution (0-15 points)
    emp_score_map = {
        'Employed': 15, 'Self-Employed': 12, 'Part-Time': 7,
        'Retired': 8, 'Unemployed': 0
    }
    approval_score += np.array([emp_score_map[e] for e in employment_status])

    # Income contribution (0-15 points)
    approval_score += np.where(annual_income >= 100000, 15,
                      np.where(annual_income >= 60000, 12,
                      np.where(annual_income >= 40000, 8,
                      np.where(annual_income >= 25000, 4, 0))))

    # Education contribution (0-10 points)
    edu_score_map = {
        'PhD': 10, 'Master': 8, 'Bachelor': 6,
        'Associate': 4, 'High School': 2
    }
    approval_score += np.array([edu_score_map[e] for e in education])

    # Add noise
    noise = np.random.normal(0, 5, size=n_rows)
    approval_score += noise

    # Threshold for approval (score out of 100)
    loan_approved = (approval_score >= 50).astype(int)

    # --- Build DataFrame ---
    df = pd.DataFrame({
        'applicant_id': [f'APP{str(i+1).zfill(5)}' for i in range(n_rows)],
        'age': age,
        'gender': gender,
        'education': education,
        'employment_status': employment_status,
        'annual_income': annual_income,
        'monthly_expenses': monthly_expenses,
        'existing_debts': existing_debts,
        'loan_amount': loan_amount,
        'loan_term': loan_term,
        'credit_score': credit_score,
        'debt_to_income_ratio': np.round(dti, 4),
        'loan_to_income_ratio': np.round(loan_amount / annual_income, 4),
        'approval_score': np.round(approval_score, 2),
        'loan_approved': loan_approved,
        'application_date': pd.date_range(
            start='2023-01-01', periods=n_rows, freq='h'
        ).strftime('%Y-%m-%d').tolist()[:n_rows]
    })

    # Introduce some realistic missing values (~2%)
    mask_indices = np.random.choice(n_rows, size=int(n_rows * 0.02), replace=False)
    df.loc[mask_indices[:len(mask_indices)//3], 'credit_score'] = np.nan
    df.loc[mask_indices[len(mask_indices)//3:2*len(mask_indices)//3], 'monthly_expenses'] = np.nan
    df.loc[mask_indices[2*len(mask_indices)//3:], 'existing_debts'] = np.nan

    # Introduce some duplicates (~0.5%)
    dup_indices = np.random.choice(n_rows, size=int(n_rows * 0.005), replace=False)
    duplicates = df.iloc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    return df


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic loan dataset')
    parser.add_argument('--rows', type=int, default=5000, help='Number of rows')
    parser.add_argument(
        '--output', type=str,
        default=os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'loan_dataset.csv'),
        help='Output CSV path'
    )
    args = parser.parse_args()

    print(f"Generating {args.rows} rows of synthetic loan data...")
    df = generate_loan_dataset(n_rows=args.rows)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    df.to_csv(args.output, index=False)
    print(f"Dataset saved to {args.output}")
    print(f"Shape: {df.shape}")
    print(f"Approval rate: {df['loan_approved'].mean():.2%}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"\nColumn types:\n{df.dtypes}")
    print(f"\nSample:\n{df.head()}")


if __name__ == '__main__':
    main()
