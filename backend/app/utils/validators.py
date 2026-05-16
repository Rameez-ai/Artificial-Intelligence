"""
Smart Loan AI - Input Validators
==================================
Validation helpers for API input data.
"""


def validate_loan_input(data: dict) -> list:
    """Validate loan application input. Returns list of errors."""
    errors = []

    # Age
    age = data.get('age')
    if age is None or not isinstance(age, (int, float)):
        errors.append("Age is required and must be a number")
    elif age < 18 or age > 100:
        errors.append("Age must be between 18 and 100")

    # Gender
    gender = data.get('gender')
    if gender not in ['Male', 'Female', 'Other']:
        errors.append("Gender must be Male, Female, or Other")

    # Education
    education = data.get('education')
    valid_edu = ['High School', 'Associate', 'Bachelor', 'Master', 'PhD']
    if education not in valid_edu:
        errors.append(f"Education must be one of: {', '.join(valid_edu)}")

    # Employment
    employment = data.get('employment_status')
    valid_emp = ['Employed', 'Self-Employed', 'Unemployed', 'Part-Time', 'Retired']
    if employment not in valid_emp:
        errors.append(f"Employment status must be one of: {', '.join(valid_emp)}")

    # Annual income
    income = data.get('annual_income')
    if income is None or not isinstance(income, (int, float)):
        errors.append("Annual income is required and must be a number")
    elif income < 0:
        errors.append("Annual income cannot be negative")

    # Monthly expenses
    expenses = data.get('monthly_expenses')
    if expenses is None or not isinstance(expenses, (int, float)):
        errors.append("Monthly expenses is required and must be a number")
    elif expenses < 0:
        errors.append("Monthly expenses cannot be negative")

    # Existing debts
    debts = data.get('existing_debts')
    if debts is None or not isinstance(debts, (int, float)):
        errors.append("Existing debts is required and must be a number")
    elif debts < 0:
        errors.append("Existing debts cannot be negative")

    # Loan amount
    loan_amount = data.get('loan_amount')
    if loan_amount is None or not isinstance(loan_amount, (int, float)):
        errors.append("Loan amount is required and must be a number")
    elif loan_amount <= 0:
        errors.append("Loan amount must be positive")

    # Loan term
    loan_term = data.get('loan_term')
    if loan_term is None or not isinstance(loan_term, (int, float)):
        errors.append("Loan term is required and must be a number")
    elif loan_term <= 0:
        errors.append("Loan term must be positive")

    # Credit score
    credit_score = data.get('credit_score')
    if credit_score is None or not isinstance(credit_score, (int, float)):
        errors.append("Credit score is required and must be a number")
    elif credit_score < 300 or credit_score > 850:
        errors.append("Credit score must be between 300 and 850")

    return errors


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> list:
    """Validate password strength. Returns list of issues."""
    issues = []
    if len(password) < 6:
        issues.append("Password must be at least 6 characters")
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one digit")
    if not any(c.isalpha() for c in password):
        issues.append("Password must contain at least one letter")
    return issues
