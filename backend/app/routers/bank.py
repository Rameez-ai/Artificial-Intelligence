"""
Smart Loan AI - Bank Intelligence Router
==========================================
POST /api/bank/match      → RAG + ML bank matching
POST /api/bank/policy-chat → RAG-powered policy Q&A
GET  /api/bank/list        → All banks (no auth required for table)
"""

from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user
from services.rag_service import get_bank_match, policy_chat
import json, os

router = APIRouter()

BANKS_PATH = os.path.join(os.path.dirname(__file__), "..", "rag", "banks_raw.json")


def _load_banks():
    # Try ingested file first, fall back to original policies
    fallback = os.path.join(os.path.dirname(__file__), "..", "rag", "bank_policies.json")
    path = BANKS_PATH if os.path.exists(BANKS_PATH) else fallback
    with open(path) as f:
        return json.load(f)


# ── GET /api/bank/list ──────────────────────────────────────────────────────

@router.get("/list")
async def list_banks():
    """Return all bank policies (public — no auth needed for comparison table)."""
    try:
        banks = _load_banks()
        return {"success": True, "data": banks, "count": len(banks)}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Bank data not available. Run ingest_policies.py.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /api/bank/match ────────────────────────────────────────────────────

@router.post("/match")
async def bank_match(
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    POST /api/bank/match
    Body: { income, loan_amount, credit_score, loan_purpose, ml_probability? }
    Returns ranked bank list + best match + LLM summary.
    """
    try:
        profile = {
            "income":       body.get("income", 0),
            "loan_amount":  body.get("loan_amount", 0),
            "credit_score": body.get("credit_score", 650),
            "loan_purpose": body.get("loan_purpose", "personal"),
        }
        ml_prob = body.get("ml_probability")  # optional float 0–1

        # Optionally call internal ML predict for the profile
        if ml_prob is None:
            try:
                from services.loan_service import LoanService
                pred = LoanService.predict({
                    "annual_income":   profile["income"] * 12,
                    "loan_amount":     profile["loan_amount"],
                    "credit_score":    profile["credit_score"],
                    "loan_term":       body.get("loan_term", 36),
                    "monthly_expenses":body.get("monthly_expenses", profile["income"] * 0.4),
                    "existing_debts":  body.get("existing_debts", 0),
                    "employment_status": body.get("employment_status", "Employed"),
                    "education":       body.get("education", "Bachelor"),
                }, user_id=None)
                ml_prob = pred.get("probability")
            except Exception:
                ml_prob = None

        result = get_bank_match(profile, ml_probability=ml_prob)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /api/bank/policy-chat ──────────────────────────────────────────────

@router.post("/policy-chat")
async def bank_policy_chat(
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    POST /api/bank/policy-chat
    Body: { question, bank_name? }
    Returns RAG-augmented answer about bank policies.
    """
    question  = body.get("question", "").strip()
    bank_name = body.get("bank_name")

    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    try:
        answer = policy_chat(question, bank_name=bank_name)
        return {"success": True, "data": {"answer": answer, "bank_name": bank_name}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
