"""
Smart Loan AI - Pydantic Schemas
==================================
Request/Response models for all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ==================== AUTH ====================

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "user"
    created_at: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


# ==================== LOAN ====================

class LoanApplication(BaseModel):
    age: int = Field(..., ge=18, le=100)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")
    education: Optional[str] = None
    employment_status: str
    annual_income: Optional[float] = Field(None, ge=0)
    monthly_income: Optional[float] = Field(None, ge=0)
    monthly_expenses: float = Field(..., ge=0)
    existing_debts: Optional[float] = Field(None, ge=0)
    existing_loans: Optional[int] = None
    existing_emi: Optional[float] = Field(None, ge=0)
    loan_amount: float = Field(..., gt=0)
    loan_term: Optional[int] = None
    loan_term_months: Optional[int] = None
    credit_score: int = Field(..., ge=300, le=850)
    dependents: Optional[int] = Field(None, ge=0)
    employment_years: Optional[int] = Field(None, ge=0)
    savings_balance: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0)
    property_value: Optional[float] = Field(None, ge=0)
    missed_payments_last_year: Optional[int] = Field(None, ge=0)
    bankruptcies: Optional[int] = Field(None, ge=0)

class LoanPredictionResult(BaseModel):
    approved: bool
    probability: float
    risk_level: str
    risk_color: str
    suggestions: list
    financial_health: dict
    prediction_id: Optional[str] = None

class LoanHistoryItem(BaseModel):
    prediction_id: str
    approved: bool
    probability: float
    risk_level: str
    loan_amount: float
    created_at: str


# ==================== CHATBOT ====================

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    response: str
    message_id: Optional[str] = None
    timestamp: str

class ChatHistoryItem(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str


# ==================== BUDGET ====================

class BudgetInput(BaseModel):
    annual_income: float = Field(..., ge=0)
    monthly_expenses: float = Field(..., ge=0)
    existing_debts: float = Field(..., ge=0)
    loan_amount: Optional[float] = 0
    loan_term: Optional[int] = 12
    credit_score: Optional[int] = 650
    expense_breakdown: Optional[dict] = None

class BudgetAnalysis(BaseModel):
    health_score: float
    grade: str
    components: dict
    metrics: dict
    recommendations: list

class EMICalculation(BaseModel):
    loan_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., ge=0, le=50)
    loan_term: int = Field(..., gt=0)

class EMIResult(BaseModel):
    monthly_emi: float
    total_payment: float
    total_interest: float
    affordable: bool
    emi_to_income_ratio: float


# ==================== RECOMMENDATIONS ====================

class RecommendationResponse(BaseModel):
    recommendations: list
    user_state: dict

class RecommendationFeedback(BaseModel):
    recommendation_id: str
    helpful: bool
    action_taken: Optional[str] = None


# ==================== ADMIN ====================

class AdminStats(BaseModel):
    total_users: int
    total_predictions: int
    approval_rate: float
    total_chats: int
    model_accuracy: Optional[float] = None

class ModelStats(BaseModel):
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    training_date: str
    total_predictions: int


# ==================== GENERIC ====================

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[list] = None
