from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation


class ConversationRepository:
    """Data access layer for Conversation entities."""

    async def create(self, db: AsyncSession) -> Conversation:
        """Create a new conversation session."""
        conversation = Conversation()
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    async def get_by_id(self, db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        """Fetch a conversation by ID with messages eager-loaded."""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(
                selectinload(Conversation.messages),
                selectinload(Conversation.observations),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, status: Optional[str] = None) -> list[Conversation]:
        """List conversations, optionally filtered by status."""
        stmt = select(Conversation).order_by(Conversation.created_at.desc())
        if status:
            stmt = stmt.where(Conversation.status == status)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_metadata(
        self,
        db: AsyncSession,
        conversation_id: str,
        *,
        dominant_emotion: Optional[str] = None,
        average_stress: Optional[float] = None,
        risk_level: Optional[str] = None,
        summary: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Update conversation aggregate metadata."""
        values = {}
        if dominant_emotion is not None:
            values["dominant_emotion"] = dominant_emotion
        if average_stress is not None:
            values["average_stress"] = average_stress
        if risk_level is not None:
            values["risk_level"] = risk_level
        if summary is not None:
            values["summary"] = summary
        if status is not None:
            values["status"] = status

        if values:
            await db.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(**values)
            )

    async def mark_completed(
        self,
        db: AsyncSession,
        conversation_id: str,
        summary: str,
        dominant_emotion: str,
        average_stress: float,
        risk_level: str,
    ) -> None:
        """Mark conversation as completed with final analytics."""
        await db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(
                status="completed",
                summary=summary,
                dominant_emotion=dominant_emotion,
                average_stress=average_stress,
                risk_level=risk_level,
            )
        )
