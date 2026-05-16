"""
Smart Loan AI - Configuration
==============================
Environment-based configuration using Pydantic BaseSettings.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Smart Loan AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT
    JWT_SECRET_KEY: str = "smart-loan-ai-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440  # 24 hours

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase/serviceAccountKey.json"
    FIREBASE_PROJECT_ID: str = "smart-loan-ai"

    # Gemini API (for chatbot)
    GEMINI_API_KEY: Optional[str] = None

    # ML Model paths
    ML_MODEL_PATH: str = "ml/trained_model.pkl"
    ML_PREPROCESSOR_PATH: str = "ml/preprocessor.pkl"
    ML_FEATURES_PATH: str = "ml/feature_names.json"

    # RL Agent path
    RL_AGENT_PATH: str = "rl/trained_agent.pkl"

    # EDA paths
    EDA_REPORTS_DIR: str = "../../eda/reports"
    EDA_DATA_DIR: str = "../../eda/data"

    # CORS
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
