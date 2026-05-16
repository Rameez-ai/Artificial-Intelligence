"""
Smart Loan AI - Model Evaluation Module
========================================
Generates comprehensive evaluation metrics, plots, and reports
for trained ML models including confusion matrix, ROC curve,
precision-recall curve, and feature importance analysis.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report, average_precision_score
)


def generate_full_evaluation(model, X_test, y_test, feature_names, output_dir, model_name="Model"):
    """
    Generate comprehensive model evaluation with plots and reports.

    Args:
        model: Trained sklearn model
        X_test: Test features
        y_test: Test labels
        feature_names: List of feature names
        output_dir: Directory to save evaluation artifacts
        model_name: Name of the model for plot titles
    """
    os.makedirs(output_dir, exist_ok=True)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # 1. Classification Report
    report = classification_report(y_test, y_pred, target_names=['Rejected', 'Approved'], output_dict=True)
    report_text = classification_report(y_test, y_pred, target_names=['Rejected', 'Approved'])

    print(f"\n{'='*50}")
    print(f"  Classification Report - {model_name}")
    print(f"{'='*50}")
    print(report_text)

    # Save report
    with open(os.path.join(output_dir, 'classification_report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    with open(os.path.join(output_dir, 'classification_report.txt'), 'w') as f:
        f.write(f"Classification Report - {model_name}\n")
        f.write("=" * 50 + "\n")
        f.write(report_text)

    # 2. Confusion Matrix
    _plot_confusion_matrix(y_test, y_pred, output_dir, model_name)

    # 3. ROC Curve
    _plot_roc_curve(y_test, y_proba, output_dir, model_name)

    # 4. Precision-Recall Curve
    _plot_precision_recall_curve(y_test, y_proba, output_dir, model_name)

    # 5. Feature Importance
    if hasattr(model, 'feature_importances_'):
        _plot_feature_importance(model, feature_names, output_dir, model_name)

    # 6. Prediction Distribution
    _plot_prediction_distribution(y_proba, y_test, output_dir, model_name)

    # 7. Summary metrics
    metrics = {
        'model_name': model_name,
        'accuracy': round(accuracy_score(y_test, y_pred), 4),
        'precision': round(precision_score(y_test, y_pred), 4),
        'recall': round(recall_score(y_test, y_pred), 4),
        'f1_score': round(f1_score(y_test, y_pred), 4),
        'roc_auc': round(roc_auc_score(y_test, y_proba), 4),
        'average_precision': round(average_precision_score(y_test, y_proba), 4),
        'test_samples': int(len(y_test)),
        'true_positives': int(confusion_matrix(y_test, y_pred)[1][1]),
        'true_negatives': int(confusion_matrix(y_test, y_pred)[0][0]),
        'false_positives': int(confusion_matrix(y_test, y_pred)[0][1]),
        'false_negatives': int(confusion_matrix(y_test, y_pred)[1][0])
    }

    with open(os.path.join(output_dir, 'evaluation_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nAll evaluation artifacts saved to: {output_dir}")
    return metrics


def _plot_confusion_matrix(y_test, y_pred, output_dir, model_name):
    """Generate and save confusion matrix plot."""
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=['Rejected', 'Approved'],
        yticklabels=['Rejected', 'Approved'],
        ax=ax, linewidths=1, linecolor='black',
        annot_kws={'size': 16}
    )
    ax.set_xlabel('Predicted', fontsize=13)
    ax.set_ylabel('Actual', fontsize=13)
    ax.set_title(f'Confusion Matrix - {model_name}', fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=150)
    plt.close()


def _plot_roc_curve(y_test, y_proba, output_dir, model_name):
    """Generate and save ROC curve plot."""
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color='#2196F3', lw=2.5, label=f'{model_name} (AUC = {auc:.4f})')
    ax.plot([0, 1], [0, 1], color='gray', lw=1.5, linestyle='--', label='Random Classifier')
    ax.fill_between(fpr, tpr, alpha=0.15, color='#2196F3')
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title(f'ROC Curve - {model_name}', fontsize=15, fontweight='bold')
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'roc_curve.png'), dpi=150)
    plt.close()


def _plot_precision_recall_curve(y_test, y_proba, output_dir, model_name):
    """Generate and save precision-recall curve plot."""
    precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
    ap = average_precision_score(y_test, y_proba)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(recall, precision, color='#4CAF50', lw=2.5, label=f'{model_name} (AP = {ap:.4f})')
    ax.fill_between(recall, precision, alpha=0.15, color='#4CAF50')
    ax.set_xlabel('Recall', fontsize=12)
    ax.set_ylabel('Precision', fontsize=12)
    ax.set_title(f'Precision-Recall Curve - {model_name}', fontsize=15, fontweight='bold')
    ax.legend(loc='lower left', fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'precision_recall_curve.png'), dpi=150)
    plt.close()


def _plot_feature_importance(model, feature_names, output_dir, model_name):
    """Generate and save feature importance plot."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    # Top 15 features
    top_n = min(15, len(feature_names))
    top_indices = indices[:top_n]

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, top_n))

    bars = ax.barh(
        range(top_n),
        importances[top_indices][::-1],
        color=colors[::-1],
        edgecolor='black',
        linewidth=0.5
    )

    ax.set_yticks(range(top_n))
    ax.set_yticklabels([feature_names[i] for i in top_indices[::-1]], fontsize=11)
    ax.set_xlabel('Feature Importance', fontsize=12)
    ax.set_title(f'Feature Importance - {model_name}', fontsize=15, fontweight='bold')

    for bar, val in zip(bars, importances[top_indices][::-1]):
        ax.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                f'{val:.4f}', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importance.png'), dpi=150)
    plt.close()

    # Save feature importance as JSON
    importance_dict = {
        feature_names[i]: round(float(importances[i]), 6)
        for i in indices
    }
    with open(os.path.join(output_dir, 'feature_importance.json'), 'w') as f:
        json.dump(importance_dict, f, indent=2)


def _plot_prediction_distribution(y_proba, y_test, output_dir, model_name):
    """Generate and save prediction probability distribution plot."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for label, color, name in [(1, '#2ecc71', 'Approved'), (0, '#e74c3c', 'Rejected')]:
        mask = y_test == label
        ax.hist(y_proba[mask], bins=50, alpha=0.6, color=color,
                label=name, edgecolor='black', linewidth=0.5)

    ax.axvline(x=0.5, color='black', linestyle='--', linewidth=1.5, label='Threshold (0.5)')
    ax.set_xlabel('Predicted Probability', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(f'Prediction Probability Distribution - {model_name}', fontsize=15, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'prediction_distribution.png'), dpi=150)
    plt.close()
