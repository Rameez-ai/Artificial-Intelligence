"""
Smart Loan AI - EDA Report Generator
=====================================
Automated Exploratory Data Analysis pipeline that produces:
- Data cleaning report
- Statistical summaries
- Visualization images
- Feature importance analysis
- HTML report

Usage:
    python generate_eda.py [--input ../data/raw/loan_dataset.csv] [--output ../reports/]
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import argparse
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set consistent style
sns.set_theme(style="whitegrid", palette="husl")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 11


class EDAReportGenerator:
    """Comprehensive EDA report generator for loan dataset."""

    def __init__(self, data_path: str, output_dir: str):
        self.data_path = data_path
        self.output_dir = output_dir
        self.viz_dir = os.path.join(output_dir, 'visualizations')
        os.makedirs(self.viz_dir, exist_ok=True)
        self.df = None
        self.df_cleaned = None
        self.report = {}

    def load_data(self):
        """Load the raw dataset."""
        print("[1/6] Loading data...")
        self.df = pd.read_csv(self.data_path)
        self.report['raw_shape'] = self.df.shape
        self.report['columns'] = list(self.df.columns)
        print(f"  Loaded {self.df.shape[0]} rows, {self.df.shape[1]} columns")

    def clean_data(self):
        """Handle missing values, duplicates, outliers."""
        print("[2/6] Cleaning data...")
        df = self.df.copy()

        # --- Missing Values ---
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        self.report['missing_values'] = {
            col: {'count': int(missing[col]), 'percentage': float(missing_pct[col])}
            for col in df.columns if missing[col] > 0
        }

        # Fill numeric missing values with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)

        # Fill categorical missing values with mode
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].mode()[0], inplace=True)

        # --- Duplicates ---
        n_duplicates = df.duplicated().sum()
        self.report['duplicates'] = int(n_duplicates)
        df.drop_duplicates(inplace=True)

        # --- Outlier Detection (IQR method on numeric columns) ---
        outlier_report = {}
        exclude_cols = ['applicant_id', 'loan_approved', 'approval_score',
                        'debt_to_income_ratio', 'loan_to_income_ratio']
        for col in numeric_cols:
            if col in exclude_cols:
                continue
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            if n_outliers > 0:
                outlier_report[col] = {
                    'count': int(n_outliers),
                    'lower_bound': round(float(lower), 2),
                    'upper_bound': round(float(upper), 2)
                }
                # Cap outliers instead of removing
                df[col] = df[col].clip(lower=lower, upper=upper)

        self.report['outliers'] = outlier_report
        self.report['cleaned_shape'] = df.shape
        self.df_cleaned = df

        # Save cleaned dataset
        cleaned_path = os.path.join(os.path.dirname(self.data_path), '..', 'cleaned', 'loan_dataset_cleaned.csv')
        os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
        df.to_csv(cleaned_path, index=False)
        print(f"  Cleaned dataset saved: {df.shape}")

    def statistical_analysis(self):
        """Compute descriptive statistics and correlations."""
        print("[3/6] Statistical analysis...")
        df = self.df_cleaned
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # Descriptive statistics
        desc = df[numeric_cols].describe().round(2)
        self.report['descriptive_stats'] = desc.to_dict()

        # Additional stats
        additional = {}
        for col in numeric_cols:
            try:
                mode_val = df[col].mode()[0]
            except Exception:
                mode_val = None
            additional[col] = {
                'mean': round(float(df[col].mean()), 2),
                'median': round(float(df[col].median()), 2),
                'mode': float(mode_val) if mode_val is not None else None,
                'std': round(float(df[col].std()), 2),
                'skewness': round(float(df[col].skew()), 4),
                'kurtosis': round(float(df[col].kurtosis()), 4)
            }
        self.report['additional_stats'] = additional

        # Correlation matrix
        corr = df[numeric_cols].corr().round(3)
        self.report['correlation'] = corr.to_dict()

        # Key correlations with target
        if 'loan_approved' in numeric_cols:
            target_corr = corr['loan_approved'].drop('loan_approved').sort_values(ascending=False)
            self.report['target_correlations'] = {
                k: round(float(v), 4) for k, v in target_corr.items()
            }

    def generate_visualizations(self):
        """Generate all visualization plots."""
        print("[4/6] Generating visualizations...")
        df = self.df_cleaned

        # 1. Loan Approval Distribution (Pie Chart)
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = ['Approved', 'Rejected']
        counts = df['loan_approved'].value_counts().sort_index(ascending=False)
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.05)
        ax.pie(counts, labels=labels, autopct='%1.1f%%', colors=colors,
               explode=explode, shadow=True, startangle=90, textprops={'fontsize': 14})
        ax.set_title('Loan Approval Distribution', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '01_approval_distribution_pie.png'))
        plt.close()

        # 2. Histograms for numeric features
        numeric_features = ['age', 'annual_income', 'monthly_expenses', 'existing_debts',
                            'loan_amount', 'loan_term', 'credit_score']
        fig, axes = plt.subplots(3, 3, figsize=(18, 14))
        axes = axes.flatten()
        for i, col in enumerate(numeric_features):
            if col in df.columns:
                axes[i].hist(df[col], bins=30, color='#3498db', edgecolor='black', alpha=0.7)
                axes[i].set_title(f'Distribution of {col}', fontsize=12, fontweight='bold')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Frequency')
        # Hide empty subplots
        for j in range(len(numeric_features), len(axes)):
            axes[j].set_visible(False)
        plt.suptitle('Feature Distributions (Histograms)', fontsize=16, fontweight='bold', y=1.01)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '02_histograms.png'))
        plt.close()

        # 3. Box Plots
        fig, axes = plt.subplots(3, 3, figsize=(18, 14))
        axes = axes.flatten()
        for i, col in enumerate(numeric_features):
            if col in df.columns:
                df.boxplot(column=col, by='loan_approved', ax=axes[i])
                axes[i].set_title(f'{col} by Approval', fontsize=12)
                axes[i].set_xlabel('Loan Approved')
        for j in range(len(numeric_features), len(axes)):
            axes[j].set_visible(False)
        plt.suptitle('Box Plots by Loan Approval', fontsize=16, fontweight='bold', y=1.01)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '03_boxplots.png'))
        plt.close()

        # 4. Correlation Heatmap
        fig, ax = plt.subplots(figsize=(14, 10))
        numeric_df = df.select_dtypes(include=[np.number])
        mask = np.triu(np.ones_like(numeric_df.corr(), dtype=bool))
        sns.heatmap(numeric_df.corr(), mask=mask, annot=True, fmt='.2f',
                    cmap='RdYlBu_r', center=0, ax=ax, linewidths=0.5,
                    square=True, cbar_kws={'shrink': 0.8})
        ax.set_title('Correlation Heatmap', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '04_correlation_heatmap.png'))
        plt.close()

        # 5. Bar Charts - Approval by Category
        cat_features = ['gender', 'education', 'employment_status']
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        for i, col in enumerate(cat_features):
            if col in df.columns:
                ct = pd.crosstab(df[col], df['loan_approved'], normalize='index') * 100
                ct.columns = ['Rejected', 'Approved']
                ct.plot(kind='bar', ax=axes[i], color=['#e74c3c', '#2ecc71'], edgecolor='black')
                axes[i].set_title(f'Approval Rate by {col}', fontsize=12, fontweight='bold')
                axes[i].set_ylabel('Percentage (%)')
                axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45, ha='right')
                axes[i].legend(loc='lower right')
        plt.suptitle('Approval Rates by Categorical Features', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '05_approval_by_category.png'))
        plt.close()

        # 6. Scatter Plots
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        scatter_pairs = [
            ('annual_income', 'loan_amount'),
            ('credit_score', 'loan_amount'),
            ('annual_income', 'credit_score'),
            ('debt_to_income_ratio', 'loan_amount')
        ]
        colors = {0: '#e74c3c', 1: '#2ecc71'}
        for i, (x, y) in enumerate(scatter_pairs):
            ax = axes[i // 2][i % 2]
            for status in [0, 1]:
                subset = df[df['loan_approved'] == status]
                ax.scatter(subset[x], subset[y], c=colors[status],
                           alpha=0.3, s=10, label='Approved' if status else 'Rejected')
            ax.set_xlabel(x, fontsize=11)
            ax.set_ylabel(y, fontsize=11)
            ax.set_title(f'{x} vs {y}', fontsize=12, fontweight='bold')
            ax.legend(markerscale=3)
        plt.suptitle('Scatter Plots: Key Feature Relationships', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '06_scatter_plots.png'))
        plt.close()

        # 7. Income Distribution by Approval
        fig, ax = plt.subplots(figsize=(12, 6))
        for status, color, label in [(1, '#2ecc71', 'Approved'), (0, '#e74c3c', 'Rejected')]:
            subset = df[df['loan_approved'] == status]
            ax.hist(subset['annual_income'], bins=40, alpha=0.6, color=color,
                    label=label, edgecolor='black')
        ax.set_title('Income Distribution by Loan Approval', fontsize=16, fontweight='bold')
        ax.set_xlabel('Annual Income')
        ax.set_ylabel('Frequency')
        ax.legend(fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '07_income_by_approval.png'))
        plt.close()

        # 8. Credit Score Impact
        fig, ax = plt.subplots(figsize=(12, 6))
        credit_bins = pd.cut(df['credit_score'], bins=[299, 500, 600, 650, 700, 750, 850])
        approval_by_credit = df.groupby(credit_bins)['loan_approved'].mean() * 100
        approval_by_credit.plot(kind='bar', ax=ax, color='#3498db', edgecolor='black')
        ax.set_title('Approval Rate by Credit Score Range', fontsize=16, fontweight='bold')
        ax.set_xlabel('Credit Score Range')
        ax.set_ylabel('Approval Rate (%)')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        for i, v in enumerate(approval_by_credit):
            ax.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '08_credit_score_impact.png'))
        plt.close()

        # 9. DTI Ratio Trends
        fig, ax = plt.subplots(figsize=(12, 6))
        dti_bins = pd.cut(df['debt_to_income_ratio'], bins=10)
        approval_by_dti = df.groupby(dti_bins)['loan_approved'].mean() * 100
        approval_by_dti.plot(kind='bar', ax=ax, color='#9b59b6', edgecolor='black')
        ax.set_title('Approval Rate by Debt-to-Income Ratio', fontsize=16, fontweight='bold')
        ax.set_xlabel('Debt-to-Income Ratio')
        ax.set_ylabel('Approval Rate (%)')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '09_dti_trends.png'))
        plt.close()

        print(f"  Generated 9 visualization sets in {self.viz_dir}")

    def feature_importance(self):
        """Analyze feature importance using Random Forest."""
        print("[5/6] Feature importance analysis...")
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder

        df = self.df_cleaned.copy()

        # Encode categorical features
        le_dict = {}
        cat_cols = ['gender', 'education', 'employment_status']
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            le_dict[col] = dict(zip(le.classes_, le.transform(le.classes_)))

        feature_cols = ['age', 'gender', 'education', 'employment_status',
                        'annual_income', 'monthly_expenses', 'existing_debts',
                        'loan_amount', 'loan_term', 'credit_score',
                        'debt_to_income_ratio', 'loan_to_income_ratio']

        X = df[feature_cols].values
        y = df['loan_approved'].values

        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)

        importances = rf.feature_importances_
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': importances
        }).sort_values('importance', ascending=False)

        self.report['feature_importance'] = importance_df.set_index('feature')['importance'].to_dict()

        # Plot
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(importance_df['feature'], importance_df['importance'],
                       color=plt.cm.viridis(np.linspace(0.3, 0.9, len(importance_df))))
        ax.set_xlabel('Importance', fontsize=12)
        ax.set_title('Feature Importance (Random Forest)', fontsize=16, fontweight='bold')
        ax.invert_yaxis()
        for bar, val in zip(bars, importance_df['importance']):
            ax.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                    f'{val:.4f}', va='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.viz_dir, '10_feature_importance.png'))
        plt.close()

        # Insights
        self.report['insights'] = {
            'top_3_features': importance_df.head(3)['feature'].tolist(),
            'approval_rate': round(float(df['loan_approved'].mean()) * 100, 2),
            'avg_income_approved': round(float(
                df[df['loan_approved'] == 1]['annual_income'].mean()), 2),
            'avg_income_rejected': round(float(
                df[df['loan_approved'] == 0]['annual_income'].mean()), 2),
            'avg_credit_approved': round(float(
                df[df['loan_approved'] == 1]['credit_score'].mean()), 2),
            'avg_credit_rejected': round(float(
                df[df['loan_approved'] == 0]['credit_score'].mean()), 2),
        }
        print(f"  Top features: {importance_df.head(3)['feature'].tolist()}")

    def generate_html_report(self):
        """Generate a comprehensive HTML EDA report."""
        print("[6/6] Generating HTML report...")

        viz_files = sorted([f for f in os.listdir(self.viz_dir) if f.endswith('.png')])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Loan AI - EDA Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f0f23; color: #e0e0e0; padding: 2rem; }}
        .header {{ text-align: center; padding: 2rem; background: linear-gradient(135deg, #1a1a3e, #2d2d5e); border-radius: 16px; margin-bottom: 2rem; }}
        .header h1 {{ color: #00d4ff; font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ color: #aaa; font-size: 1.1rem; }}
        .section {{ background: #1a1a2e; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #2a2a4a; }}
        .section h2 {{ color: #00d4ff; margin-bottom: 1rem; font-size: 1.5rem; border-bottom: 2px solid #2a2a4a; padding-bottom: 0.5rem; }}
        .section h3 {{ color: #88ccff; margin: 1rem 0 0.5rem; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid #2a2a4a; }}
        th {{ background: #2a2a4a; color: #00d4ff; }}
        tr:hover {{ background: #252545; }}
        .metric {{ display: inline-block; background: #2a2a4a; padding: 1rem 1.5rem; border-radius: 8px; margin: 0.5rem; text-align: center; min-width: 150px; }}
        .metric .value {{ font-size: 1.8rem; font-weight: bold; color: #00d4ff; }}
        .metric .label {{ font-size: 0.85rem; color: #aaa; margin-top: 0.3rem; }}
        .viz img {{ width: 100%; max-width: 900px; border-radius: 8px; margin: 1rem 0; display: block; margin-left: auto; margin-right: auto; }}
        .insight {{ background: #1e3a2e; border-left: 4px solid #2ecc71; padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0; }}
        .warning {{ background: #3a2e1e; border-left: 4px solid #e67e22; padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Smart Loan AI — EDA Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>📋 Dataset Overview</h2>
        <div class="metric"><div class="value">{self.report['raw_shape'][0]}</div><div class="label">Total Rows (Raw)</div></div>
        <div class="metric"><div class="value">{self.report['raw_shape'][1]}</div><div class="label">Total Columns</div></div>
        <div class="metric"><div class="value">{self.report['cleaned_shape'][0]}</div><div class="label">Rows (Cleaned)</div></div>
        <div class="metric"><div class="value">{self.report.get('duplicates', 0)}</div><div class="label">Duplicates Removed</div></div>
        <div class="metric"><div class="value">{self.report['insights']['approval_rate']}%</div><div class="label">Approval Rate</div></div>
    </div>

    <div class="section">
        <h2>🧹 Data Cleaning Summary</h2>
        <h3>Missing Values</h3>
        <table>
            <tr><th>Column</th><th>Count</th><th>Percentage</th></tr>
            {''.join(f"<tr><td>{col}</td><td>{info['count']}</td><td>{info['percentage']}%</td></tr>" for col, info in self.report.get('missing_values', {}).items())}
        </table>

        <h3>Outliers (IQR Method)</h3>
        <table>
            <tr><th>Column</th><th>Outlier Count</th><th>Lower Bound</th><th>Upper Bound</th></tr>
            {''.join(f"<tr><td>{col}</td><td>{info['count']}</td><td>{info['lower_bound']}</td><td>{info['upper_bound']}</td></tr>" for col, info in self.report.get('outliers', {}).items())}
        </table>
    </div>

    <div class="section">
        <h2>📈 Statistical Summary</h2>
        <table>
            <tr><th>Feature</th><th>Mean</th><th>Median</th><th>Mode</th><th>Std Dev</th><th>Skewness</th></tr>
            {''.join(f"<tr><td>{col}</td><td>{info['mean']}</td><td>{info['median']}</td><td>{info['mode']}</td><td>{info['std']}</td><td>{info['skewness']}</td></tr>" for col, info in self.report.get('additional_stats', {}).items())}
        </table>
    </div>

    <div class="section">
        <h2>🎯 Key Insights</h2>
        <div class="insight">
            <strong>Top 3 Most Important Features:</strong> {', '.join(self.report['insights']['top_3_features'])}
        </div>
        <div class="insight">
            <strong>Income Impact:</strong> Average income for approved applicants (${self.report['insights']['avg_income_approved']:,.0f}) is significantly higher than rejected (${self.report['insights']['avg_income_rejected']:,.0f})
        </div>
        <div class="insight">
            <strong>Credit Score Impact:</strong> Average credit score for approved ({self.report['insights']['avg_credit_approved']:.0f}) vs rejected ({self.report['insights']['avg_credit_rejected']:.0f})
        </div>
    </div>

    <div class="section">
        <h2>🔗 Correlation with Loan Approval</h2>
        <table>
            <tr><th>Feature</th><th>Correlation</th><th>Strength</th></tr>
            {''.join(f"<tr><td>{feat}</td><td>{corr}</td><td>{'Strong' if abs(corr)>0.5 else 'Moderate' if abs(corr)>0.3 else 'Weak'}</td></tr>" for feat, corr in self.report.get('target_correlations', {}).items())}
        </table>
    </div>

    <div class="section">
        <h2>📊 Visualizations</h2>
        {''.join(f'<div class="viz"><h3>{f.replace(".png","").replace("_"," ").title()}</h3><img src="visualizations/{f}" alt="{f}"></div>' for f in viz_files)}
    </div>

    <div class="section">
        <h2>🏆 Feature Importance</h2>
        <table>
            <tr><th>Feature</th><th>Importance Score</th></tr>
            {''.join(f"<tr><td>{feat}</td><td>{score:.4f}</td></tr>" for feat, score in sorted(self.report.get('feature_importance', {}).items(), key=lambda x: x[1], reverse=True))}
        </table>
    </div>
</body>
</html>"""

        report_path = os.path.join(self.output_dir, 'eda_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Save JSON report
        json_path = os.path.join(self.output_dir, 'eda_report.json')
        with open(json_path, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)

        print(f"  HTML report: {report_path}")
        print(f"  JSON report: {json_path}")

    def run(self):
        """Execute the full EDA pipeline."""
        print("=" * 60)
        print("  Smart Loan AI - EDA Report Generator")
        print("=" * 60)
        self.load_data()
        self.clean_data()
        self.statistical_analysis()
        self.generate_visualizations()
        self.feature_importance()
        self.generate_html_report()
        print("=" * 60)
        print("  EDA Complete! All reports generated.")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Generate EDA report for loan dataset')
    parser.add_argument(
        '--input', type=str,
        default=os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'loan_dataset.csv'),
        help='Input CSV path'
    )
    parser.add_argument(
        '--output', type=str,
        default=os.path.join(os.path.dirname(__file__), '..', 'reports'),
        help='Output directory'
    )
    args = parser.parse_args()

    generator = EDAReportGenerator(args.input, args.output)
    generator.run()


if __name__ == '__main__':
    main()
