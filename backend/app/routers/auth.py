"""
Smart Loan AI - Auth Router
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from models.schemas import UserCreate, UserLogin, UserUpdate, TokenResponse, APIResponse
from services.auth_service import AuthService
from utils.jwt_handler import verify_token
from typing import Optional

router = APIRouter()


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency: Extract and verify JWT token from header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    try:
        token = authorization.replace("Bearer ", "")
        return verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def _wrap_auth_response(result: dict) -> dict:
    """Wrap raw auth result in { success, data } envelope the Android app expects."""
    return {
        "success": True,
        "data": {
            "access_token": result.get("access_token"),
            "token_type": result.get("token_type", "bearer"),
            "user": result.get("user", {})
        }
    }


# ==================== Signup / Register ====================

@router.post("/signup", response_model=None)
async def signup(user: UserCreate):
    """Register a new user account. Accessible as POST /api/auth/signup"""
    result = AuthService.signup(user.name, user.email, user.password, user.phone)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return _wrap_auth_response(result)


@router.post("/register", response_model=None)
async def register(user: UserCreate):
    """Alias: POST /api/auth/register → same as /signup (for Android compatibility)."""
    result = AuthService.signup(user.name, user.email, user.password, user.phone)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return _wrap_auth_response(result)


# ==================== Login ====================

@router.post("/login", response_model=None)
async def login(user: UserLogin):
    """Authenticate and receive JWT token."""
    result = AuthService.login(user.email, user.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return _wrap_auth_response(result)


# ==================== Profile ====================

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile. Accessible as GET /api/auth/profile"""
    result = AuthService.get_profile(current_user["user_id"])
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Alias: GET /api/auth/me → same as /profile (for Android compatibility)."""
    result = AuthService.get_profile(current_user["user_id"])
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}


@router.put("/profile")
async def update_profile(update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user profile."""
    result = AuthService.update_profile(
        current_user["user_id"],
        update.model_dump(exclude_none=True)
    )
    return {"success": True, "data": result}
