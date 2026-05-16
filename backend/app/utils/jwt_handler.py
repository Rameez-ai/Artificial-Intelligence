"""
Smart Loan AI - JWT Handler
=============================
JWT token creation, verification, and password hashing utilities.
"""

import hashlib
import hmac
import json
import base64
import time
import secrets
from datetime import datetime, timedelta
from config import settings


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _b64_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    data += '=' * padding
    return base64.urlsafe_b64decode(data)


def create_token(user_id: str, email: str, role: str = "user") -> str:
    """Create a JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.JWT_EXPIRY_MINUTES * 60
    }

    header_b64 = _b64_encode(json.dumps(header).encode())
    payload_b64 = _b64_encode(json.dumps(payload).encode())

    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = _b64_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token. Returns payload or raises ValueError."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        header_b64, payload_b64, signature_b64 = parts

        # Verify signature
        expected_sig = hmac.new(
            settings.JWT_SECRET_KEY.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        actual_sig = _b64_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid token signature")

        # Decode payload
        payload = json.loads(_b64_decode(payload_b64))

        # Check expiration
        if payload.get('exp', 0) < int(time.time()):
            raise ValueError("Token expired")

        return payload

    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid token: {e}")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, stored_hash = hashed.split(':')
        computed_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return hmac.compare_digest(computed_hash, stored_hash)
    except (ValueError, AttributeError):
        return False
