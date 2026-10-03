# backend/verify_module_10b.py
# Temporary check: confirms human-in-the-loop approval works.

import logging

from app.core.logging_config import setup_logging
from app.config.settings import get_settings
from app.models.chat import ChatRequest, ApprovalRequest
from app.services.chat_service import handle_chat_message, handle_approval_decision

settings = get_settings()
setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)

print("--- Test 1: approved search ---")
response = handle_chat_message(
    ChatRequest(message="Search the web for the current version of LangGraph.", provider="groq")
)
print("requires_approval:", response.requires_approval)
print("approval_request:", response.approval_request)

if response.requires_approval:
    final = handle_approval_decision(
        ApprovalRequest(thread_id=response.thread_id, approved=True)
    )
    print("After approval — requires_approval again:", final.requires_approval)
    print("After approval — reply:", final.reply[:200])
    print("After approval — approval_request:", final.approval_request)

    if final.requires_approval:
        final2 = handle_approval_decision(
            ApprovalRequest(thread_id=response.thread_id, approved=True)
        )
        print("After 2nd approval — reply:", final2.reply[:300])

print("\n--- Test 2: rejected search ---")
response2 = handle_chat_message(
    ChatRequest(message="Search the web for the current version of LangGraph.", provider="groq")
)
print("requires_approval:", response2.requires_approval)

if response2.requires_approval:
    final2 = handle_approval_decision(
        ApprovalRequest(thread_id=response2.thread_id, approved=False, reason="Not needed right now")
    )
    print("After rejection — reply:", final2.reply[:200])

print("\n--- Test 3: calculator (should NOT require approval) ---")
response3 = handle_chat_message(
    ChatRequest(message="What is 99999 * 88888? Use your math tool.", provider="groq")
)
print("requires_approval:", response3.requires_approval)
print("reply:", response3.reply)