from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WellnessPlan


class WellnessPlanRepository:
    """Data access layer for WellnessPlan entities."""

    async def create(
        self, db: AsyncSession, *, conversation_id: str, plan_data: dict
    ) -> WellnessPlan:
        """Store a generated wellness plan."""
        plan = WellnessPlan(
            conversation_id=conversation_id,
            plan_data=plan_data,
        )
        db.add(plan)
        return plan

    async def get_by_conversation(
        self, db: AsyncSession, conversation_id: str
    ) -> Optional[WellnessPlan]:
        """Get the wellness plan for a conversation."""
        result = await db.execute(
            select(WellnessPlan).where(WellnessPlan.conversation_id == conversation_id)
        )
        return result.scalar_one_or_none()
