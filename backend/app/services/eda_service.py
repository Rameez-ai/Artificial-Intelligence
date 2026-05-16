"""
Smart Loan AI - EDA Service
=============================
Serves pre-generated EDA reports and visualizations.
"""

import os
import json
from config import settings


class EDAService:
    """EDA report and visualization service."""

    @staticmethod
    def get_reports() -> dict:
        """Get EDA report summary."""
        reports_dir = os.path.join(os.path.dirname(__file__), '..', settings.EDA_REPORTS_DIR)
        json_path = os.path.join(reports_dir, 'eda_report.json')

        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        return {"message": "EDA reports not generated yet. Run the EDA pipeline first."}

    @staticmethod
    def get_visualizations() -> list:
        """List available visualization files."""
        viz_dir = os.path.join(os.path.dirname(__file__), '..', settings.EDA_REPORTS_DIR, 'visualizations')
        if os.path.exists(viz_dir):
            files = [f for f in os.listdir(viz_dir) if f.endswith('.png')]
            return [{'filename': f, 'path': f'/api/eda/visualization/{f}'} for f in sorted(files)]
        return []

    @staticmethod
    def get_statistics() -> dict:
        """Get statistical summary from EDA report."""
        report = EDAService.get_reports()
        return {
            'descriptive_stats': report.get('descriptive_stats', {}),
            'additional_stats': report.get('additional_stats', {}),
            'target_correlations': report.get('target_correlations', {}),
            'insights': report.get('insights', {}),
            'feature_importance': report.get('feature_importance', {})
        }

    @staticmethod
    def get_visualization_path(filename: str) -> str:
        """Get full path for a visualization file."""
        viz_dir = os.path.join(os.path.dirname(__file__), '..', settings.EDA_REPORTS_DIR, 'visualizations')
        path = os.path.join(viz_dir, filename)
        if os.path.exists(path):
            return path
        return None
