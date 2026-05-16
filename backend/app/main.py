"""
Smart Loan AI - FastAPI Main Application
==========================================
Entry point for the FastAPI backend server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize Firebase
    try:
        from firebase.client import initialize_firebase
        initialize_firebase()
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Firebase init skipped (configure credentials): {e}")

    # Load ML model
    try:
        from services.loan_service import LoanService
        LoanService.load_model()
        print("ML model loaded successfully")
    except Exception as e:
        print(f"ML model load skipped: {e}")

    # Load RL agent
    try:
        from services.rl_service import RLService
        RLService.load_agent()
        print("RL agent loaded successfully")
    except Exception as e:
        print(f"RL agent load skipped: {e}")

    yield  # App is running

    # Shutdown
    print("Shutting down Smart Loan AI")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Loan Eligibility Pre-Check Tool with Smart Chatbot",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Core routers (original) ──────────────────────────────────────────────────
from routers import auth, loan, chatbot, budget, recommendation, admin, eda

app.include_router(auth.router,           prefix="/api/auth",      tags=["Authentication"])
app.include_router(loan.router,           prefix="/api/loan",      tags=["Loan Prediction"])
app.include_router(chatbot.router,        prefix="/api/chatbot",   tags=["AI Chatbot"])
app.include_router(budget.router,         prefix="/api/budget",    tags=["Budget Analysis"])
app.include_router(recommendation.router, prefix="/api/recommend", tags=["RL Recommendations"])
app.include_router(admin.router,          prefix="/api/admin",     tags=["Admin Dashboard"])
app.include_router(eda.router,            prefix="/api/eda",       tags=["EDA Reports"])

# ── New routers (Android compatibility) ──────────────────────────────────────
from routers import financial, loan_stats, reports

app.include_router(financial.router,  prefix="/api/financial", tags=["Financial Analysis"])
app.include_router(loan_stats.router, prefix="/api/loan",      tags=["Loan Stats"])     # adds /api/loan/stats
app.include_router(reports.router,    prefix="/api/reports",   tags=["Reports"])

# ── RAG Bank Intelligence ────────────────────────────────────────────────────
from routers import bank
app.include_router(bank.router, prefix="/api/bank", tags=["Bank Intelligence"])


# ── Health endpoints ─────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "ml_model": os.path.exists(os.path.join(os.path.dirname(__file__), settings.ML_MODEL_PATH)),
            "rl_agent": os.path.exists(os.path.join(os.path.dirname(__file__), settings.RL_AGENT_PATH)),
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
