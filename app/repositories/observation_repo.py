from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIObservation


class AIObservationRepository:
    """Data access layer for AI Observation entities."""

    async def create(
        self,
        db: AsyncSession,
        *,
        conversation_id: str,
        observation_type: str,
        content: str,
        severity: Optional[str] = "info",
        related_emotions: Optional[list] = None,
        is_recurring: bool = False,
    ) -> AIObservation:
        """Record an AI observation about the conversation."""
        observation = AIObservation(
            conversation_id=conversation_id,
            observation_type=observation_type,
            content=content,
            severity=severity,
            related_emotions=related_emotions,
            is_recurring=is_recurring,
        )
        db.add(observation)
        return observation

    async def get_by_conversation(
        self, db: AsyncSession, conversation_id: str
    ) -> list[AIObservation]:
        """Get all observations for a conversation."""
        result = await db.execute(
            select(AIObservation)
            .where(AIObservation.conversation_id == conversation_id)
            .order_by(AIObservation.created_at)
        )
        return list(result.scalars().all())

    async def get_recurring(self, db: AsyncSession, conversation_id: str) -> list[AIObservation]:
        """Get recurring observations (patterns) for a conversation."""
        result = await db.execute(
            select(AIObservation).where(
                AIObservation.conversation_id == conversation_id,
                AIObservation.is_recurring.is_(True),
            )
        )
        return list(result.scalars().all())
