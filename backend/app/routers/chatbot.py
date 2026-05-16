"""
Smart Loan AI - Chatbot Router
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatMessage
from services.chatbot_service import ChatbotService
from routers.auth import get_current_user

router = APIRouter()


@router.post("/message")
async def send_message(msg: ChatMessage, current_user: dict = Depends(get_current_user)):
    """Send a message and get AI response."""
    try:
        result = ChatbotService.get_response(current_user["user_id"], msg.message)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    """Get chat history."""
    history = ChatbotService.get_history(current_user["user_id"])
    return {"success": True, "data": history}


@router.delete("/history")
async def clear_history(current_user: dict = Depends(get_current_user)):
    """Clear chat history."""
    ChatbotService.clear_history(current_user["user_id"])
    return {"success": True, "message": "Chat history cleared"}
