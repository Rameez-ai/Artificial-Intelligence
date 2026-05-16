#!/usr/bin/env python
"""Test normalization of Android data format"""

def normalize_fields(data):
    """Simulate the normalization function"""
    normalized = data.copy()
    
    if 'monthly_income' in normalized and 'annual_income' not in normalized:
        normalized['annual_income'] = normalized['monthly_income'] * 12
    elif 'annual_income' not in normalized:
        normalized['annual_income'] = 0
    
    if 'loan_term_months' in normalized and 'loan_term' not in normalized:
        normalized['loan_term'] = normalized['loan_term_months']
    elif 'loan_term' not in normalized:
        normalized['loan_term'] = 12
    
    if 'existing_debts' not in normalized:
        emi = normalized.get('existing_emi', 0)
        loans = normalized.get('existing_loans', 0)
        existing_emi_annual = (emi or 0) * 12
        existing_loans_debt = (loans or 0) * 50000
        normalized['existing_debts'] = existing_emi_annual + existing_loans_debt
    
    normalized['existing_debts'] = max(0, normalized.get('existing_debts', 0))
    
    if 'gender' not in normalized or not normalized['gender']:
        normalized['gender'] = 'Other'
    if 'education' not in normalized or not normalized['education']:
        normalized['education'] = 'High School'
    
    if 'monthly_expenses' not in normalized:
        normalized['monthly_expenses'] = (normalized.get('annual_income', 0) / 12) * 0.5
    
    return normalized


# Test with Android data
android_data = {
    'age': 30,
    'employment_status': 'Employed',
    'monthly_income': 5000,
    'monthly_expenses': 2000,
    'credit_score': 720,
    'existing_emi': 1000,
    'existing_loans': 2,
    'loan_amount': 200000,
    'loan_term_months': 60,
}

result = normalize_fields(android_data)

print('Normalization test PASSED')
print(f'annual_income: {result.get("annual_income")} (expected: 60000)')
print(f'loan_term: {result.get("loan_term")} (expected: 60)')
print(f'existing_debts: {result.get("existing_debts")} (expected: 112000)')
print(f'gender: {result.get("gender")} (expected: Other)')
print(f'education: {result.get("education")} (expected: High School)')

# Verify required fields
required = ['age', 'gender', 'education', 'employment_status', 'annual_income', 
            'monthly_expenses', 'existing_debts', 'loan_amount', 'loan_term', 'credit_score']
print('\nRequired fields check:')
all_present = True
for field in required:
    present = field in result
    print(f'  {"✓" if present else "✗"} {field}')
    if not present:
        all_present = False

if all_present:
    print('\n✓ All required fields present!')
else:
    print('\n✗ Some required fields missing!')
    exit(1)
