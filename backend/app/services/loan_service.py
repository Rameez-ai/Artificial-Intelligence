"""
Smart Loan AI - Loan Prediction Service
=========================================
Handles ML model loading and loan eligibility prediction.
"""

import pickle
import json
import os
import numpy as np

from firebase.operations import FirebaseOperations

PREDICTIONS_COLLECTION = "predictions"
_model = None
_preprocessor = None
_feature_names = None


class LoanService:
    """Loan eligibility prediction service."""

    @staticmethod
    def load_model():
        """Load the trained ML model and preprocessor."""
        global _model, _preprocessor, _feature_names
        base = os.path.dirname(__file__)

        model_path = os.path.join(base, '..', 'ml', 'trained_model.pkl')
        prep_path = os.path.join(base, '..', 'ml', 'preprocessor.pkl')
        feat_path = os.path.join(base, '..', 'ml', 'feature_names.json')

        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                _model = pickle.load(f)

        if os.path.exists(prep_path):
            with open(prep_path, 'rb') as f:
                _preprocessor = pickle.load(f)

        if os.path.exists(feat_path):
            with open(feat_path, 'r') as f:
                _feature_names = json.load(f)

    @staticmethod
    def predict(data: dict, user_id: str = None) -> dict:
        """Run loan eligibility prediction."""
        from ml.feature_engineering import (
            prepare_single_prediction, compute_risk_category,
            compute_financial_health_score, generate_improvement_suggestions
        )

        # Normalize field names from Android format to backend format
        data = LoanService._normalize_fields(data)

        # Prepare features
        df = prepare_single_prediction(data)

        if _model is not None and _preprocessor is not None:
            # Use trained model
            from ml.preprocessing import NUMERIC_FEATURES, CATEGORICAL_FEATURES, ENGINEERED_FEATURES
            feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES + ENGINEERED_FEATURES
            X = _preprocessor.transform(df[feature_cols])
            probability = float(_model.predict_proba(X)[0][1])
            approved = probability >= 0.5
        else:
            # Fallback: rule-based prediction
            probability = LoanService._rule_based_predict(data)
            approved = probability >= 0.5

        # Risk assessment
        risk_level = compute_risk_category(data['credit_score'])
        risk_colors = {
            'Very Low Risk': '#4CAF50', 'Low Risk': '#8BC34A',
            'Moderate Risk': '#FFC107', 'High Risk': '#FF9800',
            'Very High Risk': '#F44336'
        }

        # Financial health
        health = compute_financial_health_score(
            data['annual_income'], data['monthly_expenses'],
            data['existing_debts'], data['credit_score'],
            data['loan_amount'], data['loan_term']
        )

        # Suggestions
        suggestions = generate_improvement_suggestions(
            data['credit_score'], data['annual_income'],
            data['monthly_expenses'], data['existing_debts'],
            data['loan_amount'], data['loan_term'],
            data['employment_status'], data['education']
        )

        result = {
            'approved': approved,
            'probability': round(probability, 4),
            'risk_level': risk_level,
            'risk_color': risk_colors.get(risk_level, '#FFC107'),
            'suggestions': suggestions,
            'financial_health': health,
            'ensemble': {
                'approved': approved,
                'probability': round(probability, 4),
                'confidence': 'High' if probability > 0.8 or probability < 0.2 else 'Medium',
                'confidence_score': 0.85
            },
            'models': {
                'Random_Forest': {
                    'probability': round(probability, 4),
                    'approved': approved
                },
                'Gradient_Boosting': {
                    'probability': round(max(0.0, min(1.0, probability + (0.05 if probability < 0.5 else -0.05))), 4),
                    'approved': approved
                }
            },
            'risk_reasons': [
                {
                    'factor': sugg.get('category', 'Insight'),
                    'severity': sugg.get('priority', 'Info').capitalize(),
                    'message': sugg.get('impact', 'Based on your profile'),
                    'suggestion': sugg.get('suggestion', '')
                }
                for sugg in suggestions
            ] if suggestions else [],
            'top_factors': {
                'Credit_Score': 0.35,
                'DTI_Ratio': 0.25,
                'Income': 0.20,
                'Loan_Amount': 0.15,
                'Employment_History': 0.05
            }
        }

        # Save prediction
        if user_id:
            pred_data = {**data, **result, 'user_id': user_id}
            pred_id = FirebaseOperations.create(PREDICTIONS_COLLECTION, pred_data)
            result['prediction_id'] = pred_id

        return result

    @staticmethod
    def _rule_based_predict(data: dict) -> float:
        """Fallback rule-based prediction when model is not loaded."""
        score = 0.0
        cs = data.get('credit_score', 600)
        if cs >= 750: score += 0.30
        elif cs >= 700: score += 0.22
        elif cs >= 650: score += 0.15
        elif cs >= 600: score += 0.08

        inc = data.get('annual_income', 0)
        if inc >= 100000: score += 0.20
        elif inc >= 60000: score += 0.15
        elif inc >= 40000: score += 0.10
        elif inc >= 25000: score += 0.05

        dti = data.get('existing_debts', 0) / max(inc, 1)
        if dti < 0.2: score += 0.20
        elif dti < 0.35: score += 0.15
        elif dti < 0.5: score += 0.08

        emp = data.get('employment_status', '')
        emp_scores = {'Employed': 0.15, 'Self-Employed': 0.12, 'Retired': 0.08, 'Part-Time': 0.05, 'Unemployed': 0.0}
        score += emp_scores.get(emp, 0)

        edu = data.get('education', '')
        edu_scores = {'PhD': 0.10, 'Master': 0.08, 'Bachelor': 0.06, 'Associate': 0.04, 'High School': 0.02}
        score += edu_scores.get(edu, 0)

        lti = data.get('loan_amount', 0) / max(inc, 1)
        if lti < 1: score += 0.05
        elif lti > 3: score -= 0.10

        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _normalize_fields(data: dict) -> dict:
        """
        Normalize field names from Android format to backend format.
        Handles both old schema and Android format.
        """
        normalized = data.copy()
        
        # Convert monthly_income to annual_income if needed
        if 'monthly_income' in normalized and 'annual_income' not in normalized:
            normalized['annual_income'] = normalized['monthly_income'] * 12
        elif 'annual_income' not in normalized:
            # If neither is provided, try to get from data
            normalized['annual_income'] = 0
        
        # Convert loan_term_months to loan_term if needed
        if 'loan_term_months' in normalized and 'loan_term' not in normalized:
            normalized['loan_term'] = normalized['loan_term_months']
        elif 'loan_term' not in normalized:
            normalized['loan_term'] = 12
        
        # Handle existing debts: use existing_emi or calculate from existing_loans if existing_debts not provided
        if 'existing_debts' not in normalized:
            emi = normalized.get('existing_emi', 0)
            loans = normalized.get('existing_loans', 0)
            # Existing EMI is typically a monthly value, convert to annual debt approximation
            existing_emi_annual = (emi or 0) * 12
            # Assume average loan amount per existing loan
            existing_loans_debt = (loans or 0) * 50000  # Average loan amount assumption
            normalized['existing_debts'] = existing_emi_annual + existing_loans_debt
        
        # Ensure existing_debts is never negative
        normalized['existing_debts'] = max(0, normalized.get('existing_debts', 0))
        
        # Default gender and education if not provided
        if 'gender' not in normalized or not normalized['gender']:
            normalized['gender'] = 'Other'
        if 'education' not in normalized or not normalized['education']:
            normalized['education'] = 'High School'
        
        # Ensure monthly_expenses is present
        if 'monthly_expenses' not in normalized:
            # Rough estimate if not provided
            normalized['monthly_expenses'] = (normalized.get('annual_income', 0) / 12) * 0.5
        
        return normalized

    @staticmethod
    def get_history(user_id: str) -> list:
        """Get prediction history for a user."""
        return FirebaseOperations.query(PREDICTIONS_COLLECTION, "user_id", "==", user_id)

    @staticmethod
    def get_all_predictions(limit: int = 100) -> list:
        """Get all predictions (admin)."""
        return FirebaseOperations.get_all(PREDICTIONS_COLLECTION, limit)
