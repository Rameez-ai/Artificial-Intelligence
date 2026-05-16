"""
Smart Loan AI - Auth Service
==============================
Authentication and user management logic.
"""

from firebase.operations import FirebaseOperations
from utils.jwt_handler import create_token, hash_password, verify_password
from utils.validators import validate_email, validate_password


USERS_COLLECTION = "users"


class AuthService:
    """Handles user authentication and profile management."""

    @staticmethod
    def signup(name: str, email: str, password: str, phone: str = None) -> dict:
        """Register a new user."""
        # Validate email
        if not validate_email(email):
            return {"error": "Invalid email format"}

        # Validate password
        pw_issues = validate_password(password)
        if pw_issues:
            return {"error": pw_issues[0]}

        # Check if email exists
        existing = FirebaseOperations.query(USERS_COLLECTION, "email", "==", email)
        if existing:
            return {"error": "Email already registered"}

        # Create user
        user_data = {
            "name": name,
            "email": email,
            "password": hash_password(password),
            "phone": phone,
            "role": "user"
        }
        user_id = FirebaseOperations.create(USERS_COLLECTION, user_data)

        # Generate token
        token = create_token(user_id, email, "user")

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "phone": phone,
                "role": "user"
            }
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        """Authenticate a user."""
        users = FirebaseOperations.query(USERS_COLLECTION, "email", "==", email)
        if not users:
            return {"error": "Invalid email or password"}

        user = users[0]
        if not verify_password(password, user.get("password", "")):
            return {"error": "Invalid email or password"}

        token = create_token(user["id"], email, user.get("role", "user"))

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "name": user.get("name", ""),
                "email": user["email"],
                "phone": user.get("phone"),
                "role": user.get("role", "user"),
                "created_at": user.get("created_at")
            }
        }

    @staticmethod
    def get_profile(user_id: str) -> dict:
        """Get user profile."""
        user = FirebaseOperations.get(USERS_COLLECTION, user_id)
        if not user:
            return {"error": "User not found"}
        user.pop("password", None)
        return user

    @staticmethod
    def update_profile(user_id: str, data: dict) -> dict:
        """Update user profile."""
        update_data = {k: v for k, v in data.items() if v is not None and k != "password"}
        FirebaseOperations.update(USERS_COLLECTION, user_id, update_data)
        return AuthService.get_profile(user_id)

    @staticmethod
    def get_all_users(limit: int = 100) -> list:
        """Get all users (admin)."""
        users = FirebaseOperations.get_all(USERS_COLLECTION, limit)
        for u in users:
            u.pop("password", None)
        return users
