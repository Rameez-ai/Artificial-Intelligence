"""
Smart Loan AI - RAG Policy Ingestion
======================================
Loads bank_policies.json, converts each policy to rich text chunks,
embeds them using sentence-transformers, and saves a FAISS index.

Run this script once (or whenever policies are updated):
    python ingest_policies.py
"""

import json
import os
import pickle
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICIES_PATH = os.path.join(BASE_DIR, "bank_policies.json")
INDEX_PATH    = os.path.join(BASE_DIR, "policy_index.faiss")
META_PATH     = os.path.join(BASE_DIR, "policy_metadata.json")


def policy_to_text_chunks(bank: dict) -> list[dict]:
    """Convert a single bank policy dict into several rich-text chunks with metadata."""
    name = bank["bank_name"]
    full = bank.get("full_name", name)
    chunks = []

    # ── Chunk 1: Overview ────────────────────────────────────────────────────
    loan_types = ", ".join(bank.get("loan_types", []))
    overview = (
        f"{full} ({name}) offers {loan_types} loans. "
        f"Minimum monthly income required: PKR {bank['min_income']:,}. "
        f"Minimum credit score: {bank['min_credit_score']}. "
        f"Maximum loan amount: PKR {bank['max_loan_amount']:,}. "
        f"Interest rate range: {bank['interest_rate_range']}. "
        f"Maximum tenure: {bank['max_tenure_months']} months. "
        f"Processing fee: {bank.get('processing_fee', 'N/A')}."
    )
    chunks.append({"bank_name": name, "policy_type": "overview", "text": overview})

    # ── Chunk 2: Eligibility ─────────────────────────────────────────────────
    emp_types = ", ".join(bank.get("employment_types", []))
    min_emp = bank.get("minimum_employment_months", 0)
    dti = bank.get("debt_to_income_max", 0)
    guarantor = "Required" if bank.get("guarantor_required") else "Not required"
    insurance = "Required" if bank.get("insurance_required") else "Not required"
    eligibility = (
        f"{name} eligibility criteria: Accepted employment types: {emp_types}. "
        f"Minimum employment duration: {min_emp} months. "
        f"Maximum debt-to-income ratio allowed: {dti * 100:.0f}%. "
        f"Guarantor: {guarantor}. Insurance: {insurance}. "
        f"Credit score threshold: {bank['min_credit_score']}. "
        f"Income threshold: PKR {bank['min_income']:,}/month."
    )
    chunks.append({"bank_name": name, "policy_type": "eligibility", "text": eligibility})

    # ── Chunk 3: Documentation ───────────────────────────────────────────────
    docs = ", ".join(bank.get("required_documents", []))
    documentation = (
        f"{name} required documents for loan application: {docs}. "
        f"Special conditions: {bank.get('special_conditions', 'None')}."
    )
    chunks.append({"bank_name": name, "policy_type": "documentation", "text": documentation})

    # ── Chunk 4: Loan products ───────────────────────────────────────────────
    products = (
        f"{name} loan products: {loan_types}. "
        f"Interest rates: {bank['interest_rate_range']}. "
        f"Loan amounts from PKR 10,000 up to PKR {bank['max_loan_amount']:,}. "
        f"Repayment tenure up to {bank['max_tenure_months']} months. "
        f"Special conditions: {bank.get('special_conditions', 'None')}."
    )
    chunks.append({"bank_name": name, "policy_type": "products", "text": products})

    return chunks


def build_index():
    """Build FAISS index from all bank policies."""
    print("Loading bank policies...")
    with open(POLICIES_PATH, "r") as f:
        banks = json.load(f)

    # Generate text chunks
    all_chunks = []
    for bank in banks:
        all_chunks.extend(policy_to_text_chunks(bank))
    print(f"Generated {len(all_chunks)} text chunks from {len(banks)} banks.")

    # Load sentence transformer
    print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except ImportError:
        print("ERROR: sentence-transformers not installed.")
        print("Run: pip install sentence-transformers faiss-cpu")
        return

    # Embed chunks
    texts = [c["text"] for c in all_chunks]
    print("Embedding chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")

    # Build FAISS index
    print("Building FAISS index...")
    try:
        import faiss
    except ImportError:
        print("ERROR: faiss-cpu not installed. Run: pip install faiss-cpu")
        return

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine after normalisation)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, INDEX_PATH)
    print(f"FAISS index saved to {INDEX_PATH}  ({index.ntotal} vectors, dim={dim})")

    # Save metadata
    with open(META_PATH, "w") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"Metadata saved to {META_PATH}")

    # Also save raw banks for quick lookup
    banks_path = os.path.join(BASE_DIR, "banks_raw.json")
    with open(banks_path, "w") as f:
        json.dump(banks, f, indent=2)
    print(f"Raw banks saved to {banks_path}")

    print("\n[OK] Ingestion complete!")


if __name__ == "__main__":
    build_index()
