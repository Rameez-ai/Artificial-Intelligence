"""
Smart Loan AI - Model Training Script
======================================
Trains Random Forest and XGBoost classifiers on the loan dataset.
Performs hyperparameter tuning, cross-validation, and model comparison.
Saves the best model and preprocessor for production use.

Usage:
    python train_model.py [--data ../../eda/data/raw/loan_dataset.csv]
"""

import numpy as np
import pandas as pd
import pickle
import os
import json
import argparse
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)

from preprocessing import prepare_data, save_preprocessor
from model_evaluation import generate_full_evaluation


def train_random_forest(X_train, y_train):
    """
    Train Random Forest with hyperparameter tuning.

    Args:
        X_train: Preprocessed training features
        y_train: Training labels

    Returns:
        Best RandomForest model, best params, CV scores
    """
    print("\n[RF] Training Random Forest with GridSearchCV...")

    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 15, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }

    rf = RandomForestClassifier(random_state=42, n_jobs=-1)

    # Use smaller grid for faster training
    param_grid_small = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    grid_search = GridSearchCV(
        rf, param_grid_small, cv=cv, scoring='accuracy',
        n_jobs=-1, verbose=1, return_train_score=True
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    print(f"[RF] Best params: {grid_search.best_params_}")
    print(f"[RF] Best CV accuracy: {grid_search.best_score_:.4f}")

    # Cross-validation scores
    cv_scores = cross_val_score(best_model, X_train, y_train, cv=cv, scoring='accuracy')

    return best_model, grid_search.best_params_, cv_scores


def train_xgboost(X_train, y_train):
    """
    Train XGBoost (via GradientBoosting) with hyperparameter tuning.

    Args:
        X_train: Preprocessed training features
        y_train: Training labels

    Returns:
        Best XGBoost model, best params, CV scores
    """
    print("\n[XGB] Training Gradient Boosting with GridSearchCV...")

    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'min_samples_split': [2, 5],
        'subsample': [0.8, 1.0]
    }

    xgb = GradientBoostingClassifier(random_state=42)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    grid_search = GridSearchCV(
        xgb, param_grid, cv=cv, scoring='accuracy',
        n_jobs=-1, verbose=1, return_train_score=True
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    print(f"[XGB] Best params: {grid_search.best_params_}")
    print(f"[XGB] Best CV accuracy: {grid_search.best_score_:.4f}")

    cv_scores = cross_val_score(best_model, X_train, y_train, cv=cv, scoring='accuracy')

    return best_model, grid_search.best_params_, cv_scores


def compare_and_select(models: dict, X_test, y_test) -> tuple:
    """
    Compare models and select the best one.

    Args:
        models: Dict of {name: (model, params, cv_scores)}
        X_test: Test features
        y_test: Test labels

    Returns:
        (best_model_name, best_model, comparison_report)
    """
    print("\n" + "=" * 60)
    print("MODEL COMPARISON REPORT")
    print("=" * 60)

    comparison = {}

    for name, (model, params, cv_scores) in models.items():
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            'accuracy': round(accuracy_score(y_test, y_pred), 4),
            'precision': round(precision_score(y_test, y_pred), 4),
            'recall': round(recall_score(y_test, y_pred), 4),
            'f1_score': round(f1_score(y_test, y_pred), 4),
            'roc_auc': round(roc_auc_score(y_test, y_proba), 4),
            'cv_mean': round(cv_scores.mean(), 4),
            'cv_std': round(cv_scores.std(), 4),
            'best_params': params
        }
        comparison[name] = metrics

        print(f"\n{name}:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1_score']:.4f}")
        print(f"  ROC AUC:   {metrics['roc_auc']:.4f}")
        print(f"  CV Mean:   {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")

    # Select best model based on F1 score
    best_name = max(comparison, key=lambda k: comparison[k]['f1_score'])
    print(f"\n{'=' * 60}")
    print(f"SELECTED MODEL: {best_name} (F1: {comparison[best_name]['f1_score']:.4f})")
    print(f"{'=' * 60}")

    return best_name, models[best_name][0], comparison


def main():
    parser = argparse.ArgumentParser(description='Train loan prediction model')
    parser.add_argument(
        '--data', type=str,
        default=os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eda', 'data', 'raw', 'loan_dataset.csv'),
        help='Path to dataset CSV'
    )
    parser.add_argument(
        '--output', type=str,
        default=os.path.dirname(__file__),
        help='Output directory for model files'
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Smart Loan AI - Model Training Pipeline")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Prepare data
    print("\n[STEP 1] Preparing data...")
    X_train, X_test, y_train, y_test, preprocessor, feature_names = prepare_data(args.data)
    print(f"  Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"  Features: {len(feature_names)}")
    print(f"  Approval rate (train): {y_train.mean():.2%}")

    # Step 2: Train models
    print("\n[STEP 2] Training models...")
    rf_model, rf_params, rf_cv = train_random_forest(X_train, y_train)
    xgb_model, xgb_params, xgb_cv = train_xgboost(X_train, y_train)

    models = {
        'RandomForest': (rf_model, rf_params, rf_cv),
        'GradientBoosting': (xgb_model, xgb_params, xgb_cv)
    }

    # Step 3: Compare and select
    print("\n[STEP 3] Comparing models...")
    best_name, best_model, comparison = compare_and_select(models, X_test, y_test)

    # Step 4: Generate evaluation report
    print("\n[STEP 4] Generating evaluation report...")
    eval_dir = os.path.join(args.output, 'evaluation')
    os.makedirs(eval_dir, exist_ok=True)
    generate_full_evaluation(best_model, X_test, y_test, feature_names, eval_dir, best_name)

    # Step 5: Save artifacts
    print("\n[STEP 5] Saving model artifacts...")

    # Save best model
    model_path = os.path.join(args.output, 'trained_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"  Model saved: {model_path}")

    # Save preprocessor
    preprocessor_path = os.path.join(args.output, 'preprocessor.pkl')
    save_preprocessor(preprocessor, preprocessor_path)
    print(f"  Preprocessor saved: {preprocessor_path}")

    # Save feature names
    features_path = os.path.join(args.output, 'feature_names.json')
    with open(features_path, 'w') as f:
        json.dump(feature_names, f)
    print(f"  Feature names saved: {features_path}")

    # Save comparison report
    report_path = os.path.join(args.output, 'model_comparison.json')
    with open(report_path, 'w') as f:
        json.dump({
            'selected_model': best_name,
            'comparison': comparison,
            'training_date': datetime.now().isoformat(),
            'dataset': args.data,
            'train_size': X_train.shape[0],
            'test_size': X_test.shape[0],
            'n_features': len(feature_names)
        }, f, indent=2)
    print(f"  Comparison report saved: {report_path}")

    print(f"\n{'=' * 60}")
    print(f"  Training Complete!")
    print(f"  Best Model: {best_name}")
    print(f"  Accuracy: {comparison[best_name]['accuracy']:.4f}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
