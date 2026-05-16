"""
Smart Loan AI - RAG Bank Intelligence Service
================================================
Handles FAISS retrieval and LLM-augmented bank matching.
"""

import json
import os
import math
import numpy as np
from config import settings

BASE_DIR  = os.path.join(os.path.dirname(__file__), "..", "rag")
INDEX_PATH = os.path.join(BASE_DIR, "policy_index.faiss")
META_PATH  = os.path.join(BASE_DIR, "policy_metadata.json")
BANKS_PATH = os.path.join(BASE_DIR, "banks_raw.json")

_index    = None
_metadata = None
_banks    = None
_st_model = None


def _load_rag_assets():
    global _index, _metadata, _banks, _st_model
    if _index is not None:
        return True
    try:
        import faiss
        from sentence_transformers import SentenceTransformer

        if not os.path.exists(INDEX_PATH):
            return False

        _index    = faiss.read_index(INDEX_PATH)
        with open(META_PATH)  as f: _metadata = json.load(f)
        with open(BANKS_PATH) as f: _banks    = json.load(f)
        _st_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return True
    except Exception as e:
        print(f"RAG assets load failed: {e}")
        return False


def retrieve_policy_chunks(query: str, top_k: int = 8) -> list[dict]:
    """Embed query and retrieve top-k policy chunks from FAISS."""
    if not _load_rag_assets():
        return []
    import faiss

    vec = _st_model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(vec)
    scores, indices = _index.search(vec, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = _metadata[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)
    return results


def _calculate_match_score(bank: dict, profile: dict) -> dict:
    """Rule-based eligibility pre-filter against bank thresholds."""
    income       = profile.get("income", 0)
    credit_score = profile.get("credit_score", 0)
    loan_amount  = profile.get("loan_amount", 0)
    loan_purpose = profile.get("loan_purpose", "personal").lower()

    reasons   = []
    penalties = 0

    # Income check
    if income < bank["min_income"]:
        reasons.append(f"Income PKR {income:,} below minimum PKR {bank['min_income']:,}")
        penalties += 30
    # Credit score check
    if credit_score < bank["min_credit_score"]:
        reasons.append(f"Credit score {credit_score} below minimum {bank['min_credit_score']}")
        penalties += 35
    # Loan amount check
    if loan_amount > bank["max_loan_amount"]:
        reasons.append(f"Requested PKR {loan_amount:,} exceeds max PKR {bank['max_loan_amount']:,}")
        penalties += 25
    # Loan type check
    offered = [lt.lower() for lt in bank.get("loan_types", [])]
    if loan_purpose not in offered and loan_purpose != "any":
        reasons.append(f"{bank['bank_name']} does not offer {loan_purpose} loans")
        penalties += 20

    likelihood = max(0, 100 - penalties)
    qualified  = penalties == 0

    return {
        "qualified":   qualified,
        "likelihood":  likelihood,
        "disqualifiers": reasons,
    }


def get_bank_match(profile: dict, ml_probability: float = None) -> dict:
    """
    Full bank match: retrieve RAG context → build Gemini prompt → parse response.
    Falls back to rule-based if LLM unavailable.
    """
    query = (
        f"Bank loan for {profile.get('loan_purpose','personal')} loan. "
        f"Monthly income PKR {profile.get('income',0):,}. "
        f"Credit score {profile.get('credit_score',650)}. "
        f"Requested amount PKR {profile.get('loan_amount',0):,}."
    )
    chunks = retrieve_policy_chunks(query, top_k=10)

    # Load raw banks for rule-based scoring
    if not _load_rag_assets() or _banks is None:
        # Fallback: load directly
        if os.path.exists(BANKS_PATH):
            with open(BANKS_PATH) as f:
                banks = json.load(f)
        else:
            return {"error": "Bank data not ingested. Run ingest_policies.py first."}
    else:
        banks = _banks

    # Score every bank
    results = []
    for bank in banks:
        match = _calculate_match_score(bank, profile)
        likelihood = match["likelihood"]

        # Blend with ML probability if provided
        if ml_probability is not None:
            likelihood = round(0.6 * likelihood + 0.4 * ml_probability * 100)

        # RAG context boost: if bank appears in top chunks with high score, add small bonus
        rag_bonus = sum(
            c["score"] * 5
            for c in chunks
            if c["bank_name"] == bank["bank_name"]
        )
        likelihood = min(100, round(likelihood + rag_bonus))

        results.append({
            "bank_name":          bank["bank_name"],
            "full_name":          bank.get("full_name", bank["bank_name"]),
            "min_income":         bank["min_income"],
            "interest_rate_range":bank["interest_rate_range"],
            "max_loan_amount":    bank["max_loan_amount"],
            "max_tenure_months":  bank.get("max_tenure_months", 60),
            "required_documents": bank.get("required_documents", []),
            "special_conditions": bank.get("special_conditions", ""),
            "processing_fee":     bank.get("processing_fee", "N/A"),
            "approval_likelihood":likelihood,
            "qualified":          match["qualified"],
            "disqualifiers":      match["disqualifiers"],
            "loan_types":         bank.get("loan_types", []),
        })

    results.sort(key=lambda x: x["approval_likelihood"], reverse=True)
    best_match = results[0] if results else None

    # Try to enhance with Gemini
    llm_summary = _llm_bank_summary(profile, results[:5], chunks)

    return {
        "banks":       results,
        "best_match":  best_match,
        "llm_summary": llm_summary,
        "rag_chunks":  len(chunks),
    }


def policy_chat(question: str, bank_name: str = None) -> str:
    """RAG-augmented answer for bank policy questions."""
    query = question
    if bank_name:
        query = f"{bank_name}: {question}"

    chunks = retrieve_policy_chunks(query, top_k=6)
    if not chunks:
        return "I couldn't find relevant policy information. Please ensure the bank data has been ingested."

    context = "\n\n".join(
        f"[{c['bank_name']} — {c['policy_type']}]\n{c['text']}"
        for c in chunks
    )

    if settings.GEMINI_API_KEY:
        return _llm_policy_answer(question, context, bank_name)

    # Fallback: surface best chunk
    best = chunks[0]
    return (
        f"Based on {best['bank_name']} policy ({best['policy_type']}):\n\n"
        f"{best['text']}\n\n"
        f"(Tip: Configure GEMINI_API_KEY for detailed AI-powered answers.)"
    )


def _llm_policy_answer(question: str, context: str, bank_name: str = None) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        scope = f"about {bank_name}" if bank_name else "across Pakistani banks"
        prompt = (
            f"You are a Pakistani bank loan policy expert. "
            f"Answer the following question {scope} using ONLY the policy context below.\n\n"
            f"POLICY CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            f"Provide a clear, concise answer with specific figures where available."
        )
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"AI response unavailable: {e}"


def _llm_bank_summary(profile: dict, top_banks: list, chunks: list) -> str:
    """Generate an LLM summary of top bank matches."""
    if not settings.GEMINI_API_KEY:
        if top_banks:
            b = top_banks[0]
            return (
                f"Based on your profile, {b['full_name']} appears to be your best match "
                f"with {b['approval_likelihood']}% approval likelihood and rates of {b['interest_rate_range']}."
            )
        return "No suitable banks found for your profile."

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        bank_list = "\n".join(
            f"- {b['full_name']}: {b['approval_likelihood']}% likelihood, {b['interest_rate_range']}"
            for b in top_banks
        )
        context = "\n".join(c["text"] for c in chunks[:4])

        prompt = (
            f"User financial profile:\n"
            f"- Monthly income: PKR {profile.get('income',0):,}\n"
            f"- Credit score: {profile.get('credit_score',650)}\n"
            f"- Loan amount requested: PKR {profile.get('loan_amount',0):,}\n"
            f"- Loan purpose: {profile.get('loan_purpose','personal')}\n\n"
            f"Top matching banks:\n{bank_list}\n\n"
            f"Policy context:\n{context}\n\n"
            f"Write a 2-3 sentence professional summary of which bank is the best match and why, "
            f"mentioning specific rates and conditions."
        )
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        b = top_banks[0] if top_banks else {}
        return (
            f"{b.get('full_name','A bank')} offers your best match at "
            f"{b.get('approval_likelihood',0)}% likelihood."
        )
