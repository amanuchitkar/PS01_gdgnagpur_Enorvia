from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message


class MessageRepository:
    """Data access layer for Message entities."""

    async def create(
        self,
        db: AsyncSession,
        *,
        conversation_id: str,
        role: str,
        content: str,
        emotion: Optional[str] = None,
        sentiment: Optional[str] = None,
        stress_score: Optional[int] = None,
        confidence_score: Optional[float] = None,
        risk_level: Optional[str] = None,
        emotional_summary: Optional[str] = None,
        detected_concerns: Optional[list] = None,
        suggested_next_action: Optional[str] = None,
    ) -> Message:
        """Create and persist a new message with optional analysis data."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            emotion=emotion,
            sentiment=sentiment,
            stress_score=stress_score,
            confidence_score=confidence_score,
            risk_level=risk_level,
            emotional_summary=emotional_summary,
            detected_concerns=detected_concerns,
            suggested_next_action=suggested_next_action,
        )
        db.add(message)
        return message

    async def get_by_conversation(
        self, db: AsyncSession, conversation_id: str, role: Optional[str] = None
    ) -> list[Message]:
        """Get all messages for a conversation, optionally filtered by role."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        if role:
            stmt = stmt.where(Message.role == role)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_analyzed_messages(self, db: AsyncSession, conversation_id: str) -> list[Message]:
        """Get user messages that have emotion analysis data."""
        result = await db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.role == "user",
                Message.emotion.isnot(None),
            )
        )
        return list(result.scalars().all())
