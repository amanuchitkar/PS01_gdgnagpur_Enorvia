from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PDFReport


class PDFReportRepository:
    """Data access layer for PDF Report metadata."""

    async def create(
        self,
        db: AsyncSession,
        *,
        conversation_id: str,
        filename: str,
        file_path: str,
        report_type: str = "summary",
        file_size_bytes: Optional[int] = None,
        include_wellness_plan: bool = True,
        include_charts: bool = True,
    ) -> PDFReport:
        """Store PDF report metadata."""
        report = PDFReport(
            conversation_id=conversation_id,
            filename=filename,
            file_path=file_path,
            report_type=report_type,
            file_size_bytes=file_size_bytes,
            include_wellness_plan=include_wellness_plan,
            include_charts=include_charts,
        )
        db.add(report)
        return report

    async def get_by_conversation(
        self, db: AsyncSession, conversation_id: str
    ) -> list[PDFReport]:
        """Get all PDF reports for a conversation."""
        result = await db.execute(
            select(PDFReport)
            .where(PDFReport.conversation_id == conversation_id)
            .order_by(PDFReport.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, report_id: str) -> Optional[PDFReport]:
        """Get a specific report by ID."""
        result = await db.execute(
            select(PDFReport).where(PDFReport.id == report_id)
        )
        return result.scalar_one_or_none()
