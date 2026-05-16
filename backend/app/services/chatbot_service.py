"""
Smart Loan AI - Chatbot Service
=================================
AI chatbot using Gemini API with context-aware conversations.
Falls back to rule-based responses when API key is not configured.
"""

import os
import json
import time
from datetime import datetime
from firebase.operations import FirebaseOperations
from config import settings

CHATS_COLLECTION = "chat_history"

SYSTEM_PROMPT = """You are Smart Loan AI Assistant, a helpful financial advisor chatbot. 
You help users with:
- Loan eligibility questions and advice
- EMI calculations and explanations
- Budgeting tips and savings strategies
- Financial planning guidance
- Understanding loan rejection reasons
- Credit score improvement advice

Be concise, helpful, and professional. Provide actionable advice.
If asked about non-financial topics, politely redirect to financial matters.
Always be encouraging and supportive in your responses."""


class ChatbotService:
    """AI chatbot service with Gemini API integration."""

    @staticmethod
    def get_response(user_id: str, message: str) -> dict:
        """Get chatbot response for a user message."""
        timestamp = datetime.utcnow().isoformat()

        # Save user message
        FirebaseOperations.create(CHATS_COLLECTION, {
            "user_id": user_id,
            "role": "user",
            "content": message,
            "timestamp": timestamp
        })

        # Get chat history for context
        history = ChatbotService.get_history(user_id, limit=10)

        # Try Gemini API first
        if settings.GEMINI_API_KEY:
            response_text = ChatbotService._gemini_response(message, history)
        else:
            response_text = ChatbotService._rule_based_response(message)

        # Save assistant response
        resp_timestamp = datetime.utcnow().isoformat()
        msg_id = FirebaseOperations.create(CHATS_COLLECTION, {
            "user_id": user_id,
            "role": "assistant",
            "content": response_text,
            "timestamp": resp_timestamp
        })

        return {
            "response": response_text,
            "message_id": msg_id,
            "timestamp": resp_timestamp
        }

    @staticmethod
    def _gemini_response(message: str, history: list) -> str:
        """Get response from Gemini API."""
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            # Build conversation context
            context = SYSTEM_PROMPT + "\n\nConversation history:\n"
            for msg in history[-6:]:
                role = "User" if msg.get("role") == "user" else "Assistant"
                context += f"{role}: {msg.get('content', '')}\n"
            context += f"\nUser: {message}\nAssistant:"

            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=context,
                )
            except Exception as flash_err:
                print(f"Fallback to gemini-2.0-flash due to: {flash_err}")
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=context,
                )
                
            return response.text

        except Exception as e:
            print(f"Gemini API error: {e}")
            return ChatbotService._rule_based_response(message)

    @staticmethod
    def _rule_based_response(message: str) -> str:
        """Fallback rule-based chatbot responses."""
        msg = message.lower()

        # Loan-related
        if any(w in msg for w in ['loan', 'borrow', 'lending']):
            if 'eligible' in msg or 'qualify' in msg:
                return ("Loan eligibility depends on several factors:\n"
                        "• **Credit Score**: 700+ is ideal\n"
                        "• **Income**: Stable and sufficient for EMI\n"
                        "• **DTI Ratio**: Below 35% is preferred\n"
                        "• **Employment**: Stable employment history\n\n"
                        "Use our Loan Eligibility Checker to get a detailed assessment!")
            if 'reject' in msg or 'denied' in msg:
                return ("Common loan rejection reasons:\n"
                        "1. Low credit score (below 600)\n"
                        "2. High debt-to-income ratio\n"
                        "3. Insufficient income\n"
                        "4. Unstable employment\n"
                        "5. Too many recent credit inquiries\n\n"
                        "Check our suggestions to improve your profile.")
            return ("I can help with loan-related questions! Ask me about:\n"
                    "• Loan eligibility requirements\n"
                    "• Types of loans\n"
                    "• Interest rates\n"
                    "• Application process")

        # EMI
        if 'emi' in msg:
            return ("**EMI (Equated Monthly Installment)** is your fixed monthly loan payment.\n\n"
                    "Formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)\n"
                    "Where P = Principal, r = monthly rate, n = months\n\n"
                    "**Tip**: Keep EMI below 30% of monthly income for financial health.\n"
                    "Use our EMI Calculator in the Budget section!")

        # Credit score
        if 'credit' in msg and 'score' in msg:
            return ("**Tips to improve your credit score:**\n\n"
                    "1. 📅 Pay all bills on time\n"
                    "2. 💳 Keep credit utilization below 30%\n"
                    "3. 📊 Don't close old credit accounts\n"
                    "4. 🔍 Check reports for errors regularly\n"
                    "5. ⏳ Avoid multiple hard inquiries\n\n"
                    "Credit scores range from 300-850. Aim for 700+!")

        # Budget/savings
        if any(w in msg for w in ['budget', 'save', 'saving', 'expense']):
            return ("**Smart Budgeting Tips:**\n\n"
                    "📊 **50/30/20 Rule:**\n"
                    "• 50% Needs (rent, food, bills)\n"
                    "• 30% Wants (entertainment, dining)\n"
                    "• 20% Savings & debt repayment\n\n"
                    "💡 **Quick Wins:**\n"
                    "• Track every expense for a month\n"
                    "• Automate savings transfers\n"
                    "• Review subscriptions monthly\n"
                    "• Cook meals at home more often")

        # Interest rates
        if 'interest' in msg or 'rate' in msg:
            return ("**Understanding Interest Rates:**\n\n"
                    "• **Fixed Rate**: Stays the same throughout the loan\n"
                    "• **Variable Rate**: Can change with market conditions\n"
                    "• **APR**: Annual percentage rate including fees\n\n"
                    "Lower rates = less total cost. A good credit score helps get better rates!")

        # Greeting
        if any(w in msg for w in ['hello', 'hi', 'hey', 'help']):
            return ("Hello! 👋 I'm your Smart Loan AI Assistant!\n\n"
                    "I can help you with:\n"
                    "💰 Loan eligibility & advice\n"
                    "📊 EMI calculations\n"
                    "💡 Budgeting & savings tips\n"
                    "📈 Credit score improvement\n"
                    "🏦 Financial planning\n\n"
                    "What would you like to know?")

        # Default
        return ("I'm here to help with financial matters! You can ask me about:\n"
                "• Loan eligibility and requirements\n"
                "• EMI calculations\n"
                "• Credit score improvement\n"
                "• Budgeting and savings tips\n"
                "• Financial planning advice\n\n"
                "How can I assist you today?")

    @staticmethod
    def get_history(user_id: str, limit: int = 50) -> list:
        """Get chat history for a user."""
        history = FirebaseOperations.query(CHATS_COLLECTION, "user_id", "==", user_id, limit=limit)
        history.sort(key=lambda x: x.get('timestamp', ''))
        return history

    @staticmethod
    def clear_history(user_id: str) -> bool:
        """Clear chat history for a user."""
        history = FirebaseOperations.query(CHATS_COLLECTION, "user_id", "==", user_id, limit=500)
        for msg in history:
            FirebaseOperations.delete(CHATS_COLLECTION, msg['id'])
        return True

    @staticmethod
    def get_all_logs(limit: int = 100) -> list:
        """Get all chatbot logs (admin)."""
        return FirebaseOperations.get_all(CHATS_COLLECTION, limit)
