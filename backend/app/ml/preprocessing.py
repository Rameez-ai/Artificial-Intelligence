"""
Smart Loan AI - Data Preprocessing Pipeline
============================================
Handles data loading, cleaning, encoding, scaling, and train/test split.
Provides a reusable sklearn Pipeline for consistent preprocessing.
"""

import numpy as np
import pandas as pd
import pickle
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


# Feature column definitions
NUMERIC_FEATURES = [
    'age', 'annual_income', 'monthly_expenses', 'existing_debts',
    'loan_amount', 'loan_term', 'credit_score'
]

CATEGORICAL_FEATURES = ['gender', 'education', 'employment_status']

ENGINEERED_FEATURES = [
    'debt_to_income_ratio', 'loan_to_income_ratio',
    'monthly_debt_burden', 'savings_rate', 'emi_to_income_ratio'
]

TARGET = 'loan_approved'

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + ENGINEERED_FEATURES


def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """
    Load raw CSV and perform data cleaning.

    Args:
        filepath: Path to the CSV file

    Returns:
        Cleaned DataFrame
    """
    df = pd.read_csv(filepath)

    # Drop ID and derived scoring columns (not for prediction)
    drop_cols = ['applicant_id', 'approval_score', 'application_date']
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    # Handle missing values - numeric with median, categorical with mode
    for col in NUMERIC_FEATURES:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())

    for col in CATEGORICAL_FEATURES:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].mode()[0])

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Outlier capping (IQR method) for numeric features
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df[col] = df[col].clip(lower=Q1 - 1.5 * IQR, upper=Q3 + 1.5 * IQR)

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features from raw data.

    Args:
        df: Cleaned DataFrame

    Returns:
        DataFrame with engineered features added
    """
    # Debt-to-income ratio
    df['debt_to_income_ratio'] = (
        df['existing_debts'] / df['annual_income'].replace(0, 1)
    ).round(4)

    # Loan-to-income ratio
    df['loan_to_income_ratio'] = (
        df['loan_amount'] / df['annual_income'].replace(0, 1)
    ).round(4)

    # Monthly debt burden (existing + estimated EMI)
    monthly_income = df['annual_income'] / 12
    estimated_monthly_emi = df['loan_amount'] / df['loan_term'].replace(0, 1)
    df['monthly_debt_burden'] = (
        (df['existing_debts'] / 12 + estimated_monthly_emi) / monthly_income.replace(0, 1)
    ).round(4)

    # Savings rate
    df['savings_rate'] = (
        (monthly_income - df['monthly_expenses']) / monthly_income.replace(0, 1)
    ).round(4)

    # EMI to income ratio
    df['emi_to_income_ratio'] = (
        estimated_monthly_emi / monthly_income.replace(0, 1)
    ).round(4)

    return df


def build_preprocessor() -> ColumnTransformer:
    """
    Build a sklearn ColumnTransformer for feature preprocessing.

    Returns:
        Fitted ColumnTransformer pipeline
    """
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERIC_FEATURES + ENGINEERED_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )

    return preprocessor


def prepare_data(filepath: str, test_size: float = 0.2, random_state: int = 42):
    """
    Full data preparation pipeline: load, clean, engineer, split.

    Args:
        filepath: Path to raw CSV
        test_size: Fraction for test split
        random_state: Random seed

    Returns:
        Tuple of (X_train, X_test, y_train, y_test, preprocessor, feature_names)
    """
    # Load and clean
    df = load_and_clean_data(filepath)

    # Engineer features
    df = engineer_features(df)

    # Separate features and target
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + ENGINEERED_FEATURES]
    y = df[TARGET]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Build and fit preprocessor
    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    # Get feature names after transformation
    num_features = NUMERIC_FEATURES + ENGINEERED_FEATURES
    cat_features = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(
        CATEGORICAL_FEATURES
    ).tolist()
    feature_names = num_features + cat_features

    return X_train_processed, X_test_processed, y_train, y_test, preprocessor, feature_names


def save_preprocessor(preprocessor, filepath: str):
    """Save the fitted preprocessor to disk."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(preprocessor, f)


def load_preprocessor(filepath: str):
    """Load a saved preprocessor from disk."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)
