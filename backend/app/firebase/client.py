"""
Smart Loan AI - Firebase Client
================================
Firebase Admin SDK initialization and Firestore client singleton.
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

_db = None
_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    global _db, _initialized

    if _initialized:
        return _db

    cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase', 'serviceAccountKey.json')

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Use default credentials or mock for development
        try:
            firebase_admin.initialize_app()
        except Exception:
            print("WARNING: Firebase not configured. Using mock mode.")
            _initialized = True
            return None

    _db = firestore.client()
    _initialized = True
    return _db


def get_db():
    """Get Firestore client instance."""
    global _db
    if _db is None:
        initialize_firebase()
    return _db


def get_auth():
    """Get Firebase Auth instance."""
    return auth
