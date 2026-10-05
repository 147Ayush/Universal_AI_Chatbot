# backend/app/api/conversations.py
"""Conversation history endpoints — list past chats, fetch one thread's messages.

Backed by the app-level Postgres tables (app/db/models.py), populated by
chat_service.py as conversations happen. Returns empty results gracefully
if no database is configured, rather than erroring.
"""

import logging

from fastapi import APIRouter
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Conversation, Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("")
async def list_conversations():
    if AsyncSessionLocal is None:
        return []
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Conversation).order_by(Conversation.updated_at.desc()))
        convos = result.scalars().all()
        return [
            {
                "thread_id": c.thread_id,
                "title": c.title,
                "provider": c.provider,
                "model_name": c.model_name,
                "updated_at": c.updated_at,
            }
            for c in convos
        ]


@router.get("/{thread_id}/messages")
async def get_conversation_messages(thread_id: str):
    if AsyncSessionLocal is None:
        return []
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Conversation).where(Conversation.thread_id == thread_id))
        convo = result.scalar_one_or_none()
        if not convo:
            return []

        result = await db.execute(
            select(Message).where(Message.conversation_id == convo.id).order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]
